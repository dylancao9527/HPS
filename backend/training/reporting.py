from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .ml_schema import (
    BASE_TRAINING_DATASET,
    EXPORT_DATASET,
    MODEL_SCHEMA_VERSION,
    build_feature_contract_hash,
)
from .config import DOCS_DIR, MODELS_DIR, THRESHOLD_MIN_RECALL, THRESHOLD_SEARCH_MODE
from .metrics import summarize_feature_importance


def _resolve_output_dir(default_dir: Path, output_dir: str | Path | None = None) -> Path:
    target_dir = Path(output_dir) if output_dir is not None else default_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def _get_training_code_version() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def generate_report(
    baseline_metrics,
    optimized_metrics,
    feature_columns,
    optimized_model,
    dataset_summary,
    tuning_summary,
    split_summary,
    *,
    feature_ablation=None,
    multi_seed_summary=None,
    output_dir: str | Path | None = None,
):
    importance_summary = summarize_feature_importance(feature_columns, optimized_model)
    feature_imp = importance_summary["feature_importance"]

    b = baseline_metrics
    o = optimized_metrics
    report = f"""# 模型训练报告

## 一、模型概要

| 模型 | 用途 | 保存格式 |
|---|---|---|
| Prophet | 按用户历史血压生成未来7天趋势，采用用户级 Prophet 模型持久化与阈值重训 | user_prophet_models + runtime/prophet_models |
| LightGBM | 高血压风险概率分类 | txt (lgbm_model.txt) |

---

## 二、数据集摘要

| 指标 | 数值 |
|---|---|
| 训练 Profile | {dataset_summary.get("profile_name", "raw_baseline")} |
| 主数据集 | {dataset_summary["base_dataset_name"]} |
| 主数据集样本数 | {dataset_summary["base_rows"]} |
| 主数据集正样本比例 | {dataset_summary["base_pos_ratio"]:.1%} |
| 系统导出样本数 | {dataset_summary["export_rows"]} |
| 系统导出正样本比例 | {f"{dataset_summary['export_pos_ratio']:.1%}" if dataset_summary["export_pos_ratio"] is not None else "—"} |
| 合并后总样本数 | {dataset_summary["total_rows"]} |
| 正样本数 | {dataset_summary["positive_rows"]} |
| 负样本数 | {dataset_summary["negative_rows"]} |
| 总体正样本比例 | {dataset_summary["positive_ratio"]:.1%} |
| 训练集样本数 | {split_summary["train_rows"]} |
| 测试集样本数 | {split_summary["test_rows"]} |
| 调参与最终训练池样本数 | {split_summary.get("model_selection_rows", "—")} |
| 阈值验证集样本数 | {split_summary.get("threshold_valid_rows", "—")} |
| early-stop 训练样本数 | {split_summary.get("early_stop_fit_rows", "—")} |
| early-stop 验证样本数 | {split_summary.get("early_stop_valid_rows", "—")} |
| 最终重训样本数 | {split_summary.get("final_refit_rows", "—")} |
| scale_pos_weight | {tuning_summary.scale_pos_weight:.4f} |
| 缺失值策略 | {o.get("missing_value_strategy", "native")} |

"""

    if o.get("imputation_stats"):
        report += "### 缺失值填充统计\n\n| 字段 | 中位数 |\n|---|---|\n"
        for field, value in o["imputation_stats"].items():
            report += f"| {field} | {value} |\n"
        report += "\n"

    if dataset_summary["missing_summary"]:
        report += "### 缺失值摘要\n\n| 字段 | 缺失数 |\n|---|---|\n"
        for field, count in dataset_summary["missing_summary"].items():
            report += f"| {field} | {count} |\n"
        report += "\n"

    report += f"""---

## 三、LightGBM 调参对比

### 性能对比

| 指标 | Baseline | Tuned |
|---|---|---|
| Accuracy | {b["accuracy"]:.4f} | {o["accuracy"]:.4f} |
| AUC | {b["auc"]:.4f} | {o["auc"]:.4f} |
| Precision | {b["precision"]:.4f} | {o["precision"]:.4f} |
| Recall | {b["recall"]:.4f} | {o["recall"]:.4f} |
| F1 | {b["f1"]:.4f} | {o["f1"]:.4f} |
| PR-AUC | {b["pr_auc"]:.4f} | {o["pr_auc"]:.4f} |
| Brier Score | {b["brier_score"]:.4f} | {o["brier_score"]:.4f} |
| Threshold | {b["threshold"]:.2f} | {o["threshold"]:.2f} |
| Best Iteration | {b["best_iteration"]} | {o["best_iteration"]} |

### 概率校准

- ECE: `{o['calibration']['ece']:.4f}`
- 校准分桶数: `{len(o['calibration']['bins'])}`

| Bin | Count | Avg Pred | Avg True |
|---|---|---|---|
"""
    for bucket in o["calibration"]["bins"]:
        report += (
            f"| {bucket['bin']} | {bucket['count']} | {bucket['avg_pred']:.4f} | "
            f"{bucket['avg_true']:.4f} |\n"
        )

    report += f"""
### 调优方式

- 调优器：`{tuning_summary.tuner_name}`
- 参数策略：`{tuning_summary.tuning_notes or "LightGBMTunerCV official stepwise parameter tuning"}`
- 交叉验证折数：`{tuning_summary.n_splits}`
- 最优 CV AUC：`{tuning_summary.cv_auc:.4f}`
- 阈值搜索策略：`{o["threshold_selection"]["strategy"]}`
- Recall 下限：`{o["threshold_selection"]["min_recall"]}`
- 阈值候选数：`{o["threshold_selection"].get("candidate_count", "—")}`
- Recall 约束满足：`{o["threshold_selection"].get("recall_constraint_satisfied", "—")}`
- 阈值集隔离范围：`{o.get("split_summary", {}).get("threshold_isolation_scope", "—")}`
- best_iteration 来源：`{o.get("split_summary", {}).get("best_iteration_source", "—")}`

### 最优参数

| 参数 | 数值 |
|---|---|
| lambda_l1 | {o["params"].get("lambda_l1", "-")} |
| lambda_l2 | {o["params"].get("lambda_l2", "-")} |
| num_leaves | {o["params"].get("num_leaves", "-")} |
| feature_fraction | {o["params"].get("feature_fraction", "-")} |
| bagging_fraction | {o["params"].get("bagging_fraction", "-")} |
| bagging_freq | {o["params"].get("bagging_freq", "-")} |
| min_child_samples | {o["params"].get("min_child_samples", "-")} |
| max_depth | {o["params"].get("max_depth", "-")} |
| min_gain_to_split | {o["params"].get("min_gain_to_split", "-")} |
| min_sum_hessian_in_leaf | {o["params"].get("min_sum_hessian_in_leaf", "-")} |
| extra_trees | {o["params"].get("extra_trees", "-")} |

### 最终测试集混淆矩阵

| 指标 | 数值 |
|---|---|
| TN | {o["confusion_matrix"]["tn"]} |
| FP | {o["confusion_matrix"]["fp"]} |
| FN | {o["confusion_matrix"]["fn"]} |
| TP | {o["confusion_matrix"]["tp"]} |

"""
    report += f"""

---

## 四、特征重要性

| 排名 | 特征 | 重要性 (gain) | 占总 gain 比例 |
|---|---|---|---|
"""
    for idx, item in enumerate(feature_imp, 1):
        report += (
            f"| {idx} | {item['feature']} | {item['gain']:.1f} | "
            f"{item['gain_share']:.1%} |\n"
        )

    report += f"""

---

## 五、特征增益解读

- 血压特征总 gain 占比：`{importance_summary["bp_gain_share"]:.1%}`
- Top3 特征 gain 占比：`{importance_summary["top3_gain_share"]:.1%}`
- 低信号特征：`{", ".join(importance_summary["low_signal_features"]) if importance_summary["low_signal_features"] else "无"}`

"""
    for line in importance_summary["interpretation"]:
        report += f"- {line}\n"

    if feature_ablation:
        report += "\n---\n\n## 六、特征消融实验\n\n| 方案 | 特征列 | AUC | PR-AUC | Brier Score | Threshold |\n|---|---|---|---|---|---|\n"
        for item in feature_ablation:
            report += (
                f"| {item['name']} | {', '.join(item['columns'])} | {item['auc']:.4f} | "
                f"{item['pr_auc']:.4f} | {item['brier_score']:.4f} | {item['threshold']:.2f} |\n"
            )

    if multi_seed_summary:
        report += "\n---\n\n## 七、多随机种子稳定性审计\n\n"
        report += (
            f"- Seed 数量：`{multi_seed_summary['seed_count']}`\n"
            f"- AUC 均值 / 标准差：`{multi_seed_summary['auc_mean']:.4f}` / `{multi_seed_summary['auc_std']:.4f}`\n"
            f"- PR-AUC 均值 / 标准差：`{multi_seed_summary['pr_auc_mean']:.4f}` / `{multi_seed_summary['pr_auc_std']:.4f}`\n"
            f"- Brier Score 均值 / 标准差：`{multi_seed_summary['brier_mean']:.4f}` / `{multi_seed_summary['brier_std']:.4f}`\n"
            f"- Threshold 范围：`{multi_seed_summary['threshold_min']:.4f}` ~ `{multi_seed_summary['threshold_max']:.4f}`\n\n"
        )
        report += "| Seed | AUC | PR-AUC | Brier Score | Threshold |\n|---|---|---|---|---|\n"
        for item in multi_seed_summary["runs"]:
            report += (
                f"| {item['seed']} | {item['auc']:.4f} | {item['pr_auc']:.4f} | "
                f"{item['brier_score']:.4f} | {item['threshold']:.4f} |\n"
            )

    report += f"""

---

## 八、训练与更新流程

1. 主训练集使用 `{BASE_TRAINING_DATASET}`
2. 管理员可导出 `{EXPORT_DATASET}` 作为系统样本补充
3. 运行 `cd backend && uv run python scripts/train_models.py`；如需显式控制随机性，可追加 `--seed <int>` 或 `--random-seed`
4. 脚本自动合并主数据集与系统导出样本，并先拆分测试集和独立阈值验证集
5. LightGBMTunerCV、early stopping 和最终重训只使用阈值集之外的训练池；模型参数冻结后再用独立阈值集搜索分类阈值
6. 默认训练会通过候选产物目录发布到 `backend/ml_models/`，并同步更新唯一的 canonical 报告与模型配置

---

## 九、Prophet 性能优化说明

本项目中的 Prophet 模型持久化在用户维度进行：预测链路会根据新增血压自然日数量判断是否重训，未达到阈值时复用已有模型重新生成本次未来7天血压趋势。为平衡预测效果与交互效率，系统默认仅截取最近 `90` 天的日均血压数据参与训练，并同步返回 `total_history_days` 与 `history_window_capped` 字段说明本次训练窗口情况。
"""

    report_path = _resolve_output_dir(DOCS_DIR, output_dir) / "model_report.md"
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"\n  [OK] 训练报告已生成: {report_path}")
    return report_path


def save_final_model(
    model,
    feature_columns,
    categorical_features,
    threshold,
    *,
    bp_meds_policy,
    label_mode,
    dataset_hash,
    missing_value_strategy,
    threshold_search_mode=THRESHOLD_SEARCH_MODE,
    threshold_min_recall=THRESHOLD_MIN_RECALL,
    output_dir: str | Path | None = None,
):
    target_dir = _resolve_output_dir(MODELS_DIR, output_dir)
    model_path = target_dir / "lgbm_model.txt"
    config_path = target_dir / "model_config.json"
    model.save_model(str(model_path))
    best_iteration = model.best_iteration or model.current_iteration()

    config = {
        "feature_columns": feature_columns,
        "categorical_features": categorical_features,
        "best_iteration": best_iteration,
        "classification_threshold": threshold,
        "threshold_search_mode": threshold_search_mode,
        "threshold_min_recall": threshold_min_recall,
        "base_dataset": BASE_TRAINING_DATASET,
        "schema_version": MODEL_SCHEMA_VERSION,
        "feature_contract_hash": build_feature_contract_hash(
            feature_columns,
            categorical_features,
        ),
        "bp_meds_policy": bp_meds_policy,
        "label_mode": label_mode,
        "dataset_hash": dataset_hash,
        "missing_value_strategy": missing_value_strategy,
        "training_code_version": _get_training_code_version(),
    }
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)

    print(f"\n  [OK] LightGBM 模型: {model_path}")
    print(f"  [OK] 模型配置: {config_path}")


def save_training_meta(
    dataset_summary,
    split_summary,
    baseline_metrics,
    tuning_summary,
    optimized_metrics,
    feature_columns,
    optimized_model,
    *,
    feature_ablation=None,
    multi_seed_summary=None,
    output_dir: str | Path | None = None,
):
    meta_path = _resolve_output_dir(MODELS_DIR, output_dir) / "training_meta.json"
    feature_summary = summarize_feature_importance(feature_columns, optimized_model)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset_summary": dataset_summary,
        "split_summary": split_summary,
        "baseline_metrics": baseline_metrics,
        "tuning_summary": tuning_summary.to_dict() if hasattr(tuning_summary, "to_dict") else tuning_summary,
        "optimized_metrics": optimized_metrics,
        "missing_value_strategy": optimized_metrics.get("missing_value_strategy", "native"),
        "imputation_stats": optimized_metrics.get("imputation_stats"),
        "feature_importance_summary": feature_summary,
        "feature_ablation": feature_ablation or [],
        "multi_seed_summary": multi_seed_summary,
    }
    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    print(f"  [OK] 训练元信息: {meta_path}")
