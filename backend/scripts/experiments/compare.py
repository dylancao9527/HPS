"""
对照实验比较脚本

用法:
  # 先跑 baseline 训练，保存到独立目录，不覆盖生产模型
  uv run python scripts/train_models.py --params scripts/experiments/baseline.json --run-name baseline-recall --no-promote

  # 再跑 experiment 训练，保存到独立目录
  uv run python scripts/train_models.py --params scripts/experiments/experiment.json --run-name experiment-f1 --no-promote

  # 生成对比报告
  uv run python scripts/experiments/compare.py --baseline ml_runs\\20260516-220000-baseline-recall --experiment ml_runs\\20260516-221000-experiment-f1
  uv run python scripts/experiments/compare.py --output ..\\docs\\reports\\comparison_report.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BASELINE = SCRIPT_DIR / "baseline_result.json"
DEFAULT_EXPERIMENT = SCRIPT_DIR / "experiment_result.json"

METRIC_LABELS = [
    ("AUC", "auc"),
    ("Recall", "recall"),
    ("Precision", "precision"),
    ("F1", "f1"),
    ("PR-AUC", "pr_auc"),
    ("Brier Score", "brier_score"),
    ("Accuracy", "accuracy"),
    ("Threshold", "threshold"),
]


def _arrow(diff: float) -> str:
    if diff > 0.005:
        return "↑"
    if diff < -0.005:
        return "↓"
    return "≈"


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _diff_params(baseline_json: dict, experiment_json: dict) -> list[tuple[str, str, str]]:
    """返回两组参数中有差异的字段列表."""
    skip = {"seed"}
    all_keys = sorted(set(list(baseline_json.keys()) + list(experiment_json.keys())) - skip)
    rows = []
    for k in all_keys:
        vb = baseline_json.get(k)
        ve = experiment_json.get(k)
        if vb != ve:
            rows.append((k, _fmt(vb), _fmt(ve)))
    return rows


def build_comparison(
    baseline: dict,
    experiment: dict,
    baseline_source: str = "baseline_result.json",
    experiment_source: str = "experiment_result.json",
) -> str:
    lines: list[str] = []

    lines.append("# 训练对照实验报告\n")
    lines.append(f"- Baseline 结果: `{baseline_source}`")
    lines.append(f"- Experiment 结果: `{experiment_source}`")
    lines.append("")

    # --- 参数差异 ---
    bp = _load_params(SCRIPT_DIR / "baseline.json")
    ep = _load_params(SCRIPT_DIR / "experiment.json")
    if bp and ep:
        param_diffs = _diff_params(bp, ep)
        if param_diffs:
            lines.append("## 一、参数差异\n")
            lines.append("| 参数 | Baseline | Experiment |")
            lines.append("|---|---|---|")
            for k, vb, ve in param_diffs:
                lines.append(f"| {k} | {vb} | {ve} |")
            lines.append("")

    # --- 数据集概况 ---
    bd = baseline.get("dataset_summary", {})
    ed = experiment.get("dataset_summary", {})
    lines.append("## 二、数据集\n")
    lines.append("| 项目 | Baseline | Experiment |")
    lines.append("|---|---|---|")
    lines.append(f"| 数据集 | {bd.get('base_dataset_name', '—')} | {ed.get('base_dataset_name', '—')} |")
    lines.append(f"| 样本数 | {bd.get('total_rows', '—')} | {ed.get('total_rows', '—')} |")
    lines.append(f"| 正样本比例 | {_fmt_pct(bd.get('positive_ratio'))} | {_fmt_pct(ed.get('positive_ratio'))} |")
    lines.append("")

    # --- Baseline 阶段对比 ---
    bm = baseline.get("baseline_metrics", {})
    em = experiment.get("baseline_metrics", {})
    if bm and em:
        lines.append("## 三、Baseline 模型对比\n")
        lines.append("| 指标 | Baseline | Experiment | 差异 |")
        lines.append("|---|---:|---:|---|")
        for label, key in METRIC_LABELS:
            vb, ve = bm.get(key), em.get(key)
            if vb is not None and ve is not None:
                diff = ve - vb
                lines.append(f"| {label} | {_fmt(vb)} | {_fmt(ve)} | {diff:+.4f} {_arrow(diff)} |")
        lines.append(f"| Best Iteration | {bm.get('best_iteration', '—')} | {em.get('best_iteration', '—')} | |")
        lines.append("")

    # --- Tuned 阶段对比 ---
    bo = baseline.get("optimized_metrics", {})
    eo = experiment.get("optimized_metrics", {})
    lines.append("## 四、Tuned 模型对比（核心结果）\n")
    lines.append("| 指标 | Baseline | Experiment | 差异 |")
    lines.append("|---|---:|---:|---|")
    for label, key in METRIC_LABELS:
        vb, ve = bo.get(key), eo.get(key)
        if vb is not None and ve is not None:
            diff = ve - vb
            lines.append(f"| {label} | {_fmt(vb)} | {_fmt(ve)} | {diff:+.4f} {_arrow(diff)} |")
    lines.append(f"| Best Iteration | {bo.get('best_iteration', '—')} | {eo.get('best_iteration', '—')} | |")
    lines.append("")

    # --- CV AUC ---
    bt = baseline.get("tuning_summary", {})
    et = experiment.get("tuning_summary", {})
    if bt and et:
        diff = et.get("cv_auc", 0) - bt.get("cv_auc", 0)
        lines.append("## 五、TunerCV 调参对比\n")
        lines.append(f"| 项目 | Baseline | Experiment | 差异 |")
        lines.append(f"|---|---:|---:|---|")
        lines.append(f"| CV AUC | {_fmt(bt.get('cv_auc'))} | {_fmt(et.get('cv_auc'))} | {diff:+.4f} {_arrow(diff)} |")
        lines.append(f"| Best Iteration | {bt.get('best_iteration', '—')} | {et.get('best_iteration', '—')} | |")
        lines.append("")

        # tuned params diff
        tp_b = bt.get("tuned_params", {})
        tp_e = et.get("tuned_params", {})
        all_keys = sorted(set(list(tp_b.keys()) + list(tp_e.keys())))
        if all_keys:
            lines.append("### 调优参数差异\n")
            lines.append("| 参数 | Baseline | Experiment |")
            lines.append("|---|---|---|")
            for k in all_keys:
                vb = tp_b.get(k, "—")
                ve = tp_e.get(k, "—")
                lines.append(f"| {k} | {_fmt(vb)} | {_fmt(ve)} |")
            lines.append("")

    # --- 混淆矩阵 ---
    bc = bo.get("confusion_matrix", {})
    ec = eo.get("confusion_matrix", {})
    if bc and ec:
        lines.append("## 六、混淆矩阵对比\n")
        lines.append("| 指标 | Baseline | Experiment |")
        lines.append("|---|---:|---:|")
        for k in ["tn", "fp", "fn", "tp"]:
            lines.append(f"| {k.upper()} | {bc.get(k, '—')} | {ec.get(k, '—')} |")
        lines.append("")

    # --- 特征重要性 ---
    bf = baseline.get("feature_importance_summary", {}).get("feature_importance", [])
    ef = experiment.get("feature_importance_summary", {}).get("feature_importance", [])
    if bf and ef:
        bf_map = {f["feature"]: f for f in bf}
        ef_map = {f["feature"]: f for f in ef}
        all_features = list(dict.fromkeys([f["feature"] for f in bf] + [f["feature"] for f in ef]))
        lines.append("## 七、特征重要性对比\n")
        lines.append("| 特征 | Baseline gain% | Experiment gain% |")
        lines.append("|---|---:|---:|")
        for feat in all_features:
            vb = bf_map.get(feat, {}).get("gain_share")
            ve = ef_map.get(feat, {}).get("gain_share")
            lines.append(f"| {feat} | {_fmt_pct(vb)} | {_fmt_pct(ve)} |")
        bp_b = baseline.get("feature_importance_summary", {}).get("bp_gain_share")
        bp_e = experiment.get("feature_importance_summary", {}).get("bp_gain_share")
        lines.append(f"| **血压合计** | **{_fmt_pct(bp_b)}** | **{_fmt_pct(bp_e)}** |")
        lines.append("")

    return "\n".join(lines)


def _fmt_pct(v) -> str:
    if v is None:
        return "—"
    return f"{v:.1%}"


def _load_params(path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _load_result(path_value: str) -> dict:
    path = Path(path_value)
    if path.is_dir():
        path = path / "training_meta.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="对照实验比较")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="baseline 结果 JSON 或 run 目录")
    parser.add_argument("--experiment", default=str(DEFAULT_EXPERIMENT), help="experiment 结果 JSON 或 run 目录")
    parser.add_argument("--output", default=None, help="输出 markdown 文件路径（不填则打印到终端）")
    args = parser.parse_args()

    baseline = _load_result(args.baseline)
    experiment = _load_result(args.experiment)

    report = build_comparison(
        baseline,
        experiment,
        baseline_source=args.baseline,
        experiment_source=args.experiment,
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"对比报告已生成: {out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
