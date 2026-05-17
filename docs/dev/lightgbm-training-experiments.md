---
doc_type: dev-guide
slug: lightgbm-training-experiments
component: lightgbm-training
status: current
summary: LightGBM training experiments, comparison runs, and production promotion workflow.
tags: [lightgbm, training, experiments, recall-priority, model-promotion]
last_reviewed: "2026-05-17"
---

# LightGBM 训练实验开发者指南

## 概述

LightGBM 训练脚本现在同时支持生产训练和对照实验。实验训练应优先写入 `backend/ml_runs/`，等指标确认后再显式发布到 `backend/ml_models/`。当前生产口径以召回优先为主，所有论文/报告用对照实验参数都应使用 `threshold_search_mode=recall_priority`，再通过 `threshold_min_recall`、学习率、训练轮数、缺失值策略或 BPMeds 处理策略拉开实验差异。

## 前置依赖

- 后端依赖由 `uv` 管理，命令在 `backend/` 下运行。
- 训练脚本不会自动导出系统样本；如需合并系统训练样本，先运行 `uv run python scripts/export_training_data.py`。
- 训练参数文件位于 `backend/scripts/experiments/`。
- 实验产物位于 `backend/ml_runs/<timestamp>-<run-name>/`。
- 生产模型位于 `backend/ml_models/`，上一版发布备份位于 `backend/ml_models_previous/`。

## 快速上手

```powershell
cd backend

uv run python scripts/train_models.py `
  --params scripts/experiments/baseline.json `
  --run-name recall-baseline `
  --no-promote

uv run python scripts/train_models.py `
  --params scripts/experiments/experiment.json `
  --run-name recall-min85 `
  --no-promote

Get-ChildItem ml_runs | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name,LastWriteTime
```

确认结果后再发布：

```powershell
cd backend
uv run python scripts/train_models.py `
  --params scripts/experiments/experiment.json `
  --run-name final-recall-min85 `
  --promote
```

## 核心概念

### Run 目录

`--run-name` 会创建独立 run 目录，并保存 `params.json`、`training_meta.json`、`model_report.md`、`model_config.json` 和 `lgbm_model.txt`。做实验时必须配合 `--no-promote`，避免临时实验覆盖生产模型。

### 两阶段发布

`--promote` 会先生成候选 run，再把候选目录中的 `lgbm_model.txt`、`model_config.json` 和 `training_meta.json` 发布到 `backend/ml_models/`，并把候选报告复制为 `docs/reports/model_report.md`。旧生产目录会移动到 `backend/ml_models_previous/`，用于本地回看和回滚参考。

### 阈值隔离

训练流程会先从训练集切出独立 threshold holdout。LightGBMTunerCV、early stopping 和最终重训只使用阈值集之外的训练池；模型参数冻结后，再用 threshold holdout 搜索分类阈值。这个隔离用于避免阈值搜索污染模型选择。

## 参数组

| 文件 | 目的 | 关键差异 |
|---|---|---|
| `baseline.json` | 默认 recall 对照组 | `threshold_min_recall=0.75` |
| `experiment.json` | 当前生产候选 | `threshold_min_recall=0.85` |
| `low_lr_long_recall.json` | 低学习率长训练 | `learning_rate=0.03`，更长训练和早停 |
| `fast_lr_short_recall.json` | 高学习率快停 | `learning_rate=0.1`，更短训练和早停 |
| `median_impute_recall.json` | 缺失值策略对照 | `missing_value_strategy=median_impute` |
| `bpmeds_observed_recall.json` | 用药信号对照 | `bp_meds_policy=observed` |

## 选择生产模型

召回优先任务下，先看测试集 Recall 是否达到该组配置的 `threshold_min_recall`，再比较 F1、AUC、PR-AUC、Brier Score 和阈值合理性。AUC 高但 Recall/F1 明显落后的模型不适合作为当前生产模型。

2026-05-17 的六组对照中，`recall-min85` 被选为生产模型：

| 指标 | 数值 |
|---|---:|
| AUC | 0.9498 |
| PR-AUC | 0.8706 |
| Brier Score | 0.0850 |
| Precision | 0.8246 |
| Recall | 0.8935 |
| F1 | 0.8577 |
| Threshold | 0.6503 |
| TP/FP/FN/TN | 235/50/28/535 |

## 常见场景

### 做一轮新的 recall-priority 参数对照

1. 从 `baseline.json` 复制一份新参数文件。
2. 保持 `threshold_search_mode=recall_priority`。
3. 只改 1-2 个明确变量，例如 `threshold_min_recall` 或 `learning_rate`。
4. 用 `--run-name <name> --no-promote` 训练。
5. 读取 run 目录中的 `training_meta.json` 汇总指标。
6. 把结论写入 `docs/reports/comparison_report.md`。

### 晋升生产模型

1. 确认候选 run 的 `params.json` 与预期一致。
2. 确认 `training_meta.json` 中 `optimized_metrics.threshold_selection.strategy=recall_priority`。
3. 用同一参数文件重新运行 `--promote`。
4. 核对 `backend/ml_models/model_config.json` 中的 `classification_threshold`、`threshold_search_mode` 和 `threshold_min_recall`。
5. 运行 `uv run pytest tests\training -q`，必要时运行完整 `uv run pytest`。

## 已知限制与注意事项

- `backend/ml_runs/`、`backend/ml_models/` 和 `backend/ml_models_previous/` 是本地生成产物，不纳入版本控制。
- `compare.py` 适合两组 run 的详细对比；多组汇总目前仍需要人工或临时脚本读取各 run 的 `training_meta.json`。
- `bpmeds_observed_recall.json` 在 2026-05-17 实验中 AUC 更高，但 Recall/F1 不适合当前召回优先生产目标。

## 相关文档

- `docs/training_guide.md`
- `docs/reports/comparison_report.md`
- `docs/reports/model_report.md`
- `.codestable/audits/2026-05-17-lightgbm-training-script/fix-note.md`
- `.codestable/compound/2026-05-17-learning-lightgbm-recall-priority-selection.md`
- `.codestable/compound/2026-05-17-trick-lightgbm-safe-experiment-promotion.md`
