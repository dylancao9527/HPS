---
doc_type: learning
track: knowledge
date: "2026-05-17"
slug: lightgbm-recall-priority-selection
component: lightgbm-training
tags: [lightgbm, recall-priority, threshold, model-selection, training]
---

## 背景

高血压风险预测的 LightGBM 模型用于健康管理辅助场景。当前业务目标更偏向少漏报高风险用户，因此对照实验不能再用一组 `recall_priority` 对一组 `f1` 来证明差异，而应让所有实验统一使用 `recall_priority`，再改变其他参数形成可解释的对照。

## 指导原则

- 对照实验参数文件统一设置 `threshold_search_mode=recall_priority`。
- 在同一标签口径下比较模型，当前保持 `label_mode=diagnosis_plus_rule`。
- 先用 `--run-name ... --no-promote` 生成独立 run，确认指标后再 `--promote`。
- 选择生产模型时，先看测试集 Recall 是否达到该组 `threshold_min_recall`，再比较 F1、AUC、PR-AUC、Brier Score 和阈值是否合理。
- AUC 高但 Recall/F1 明显低的模型，不适合作为当前召回优先生产模型。

## 为什么重要

阈值策略会显著改变 Recall、Precision 和 F1。如果一组使用 `f1`，另一组使用 `recall_priority`，对照结果会混入阈值目标差异，难以判断模型参数本身是否更好。统一阈值策略后，实验结论更容易复现，也更容易解释给论文和系统报告使用。

## 何时适用

- 调整 LightGBM 训练参数。
- 做论文/报告用对照实验。
- 决定是否发布新的 `backend/ml_models/` 生产模型。
- 复查 `docs/reports/comparison_report.md` 中的模型选择依据。

## 示例

2026-05-17 六组实验均采用 `recall_priority`：

| 实验 | 关键差异 | Recall | F1 | AUC | Brier |
|---|---|---:|---:|---:|---:|
| `recall-baseline` | `threshold_min_recall=0.75` | 0.7757 | 0.8016 | 0.9498 | 0.0850 |
| `recall-min85` | `threshold_min_recall=0.85` | 0.8935 | 0.8577 | 0.9498 | 0.0850 |
| `recall-low-lr-long` | `learning_rate=0.03` | 0.8327 | 0.8295 | 0.9501 | 0.0993 |
| `recall-fast-lr-short` | `learning_rate=0.10` | 0.7719 | 0.7976 | 0.9491 | 0.0831 |
| `recall-median-impute` | `missing_value_strategy=median_impute` | 0.8403 | 0.8355 | 0.9493 | 0.0821 |
| `recall-bpmeds-observed` | `bp_meds_policy=observed` | 0.7605 | 0.7905 | 0.9555 | 0.0773 |

最终选择 `recall-min85` 发布为生产模型。它不是 AUC 最高的一组，但它的 Recall 和 F1 同时最高，且概率质量没有明显恶化。

## 相关文档

- `docs/dev/lightgbm-training-experiments.md`
- `docs/training_guide.md`
- `docs/reports/comparison_report.md`
- `docs/reports/model_report.md`
- `.codestable/audits/2026-05-17-lightgbm-training-script/fix-note.md`
