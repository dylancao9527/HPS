# Recall Priority 对照实验报告

- 实验时间: 2026-05-17
- 共同设置: `threshold_search_mode=recall_priority`，`seed=42`，`label_mode=diagnosis_plus_rule`
- 选择结论: `20260517-143320-recall-min85` 作为生产候选，原因是 Recall 和 F1 同时最高，AUC 与 Brier 保持健康。

## 一、实验结果总览

| Run | min_recall | learning_rate | missing | BPMeds | AUC | PR-AUC | Brier | Precision | Recall | F1 | Threshold | TP/FP/FN/TN |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 20260517-143158-recall-baseline | 0.75 | 0.05 | native | neutralized | 0.9498 | 0.8706 | 0.0850 | 0.8293 | 0.7757 | 0.8016 | 0.7019 | 204/42/59/543 |
| 20260517-143320-recall-min85 | 0.85 | 0.05 | native | neutralized | 0.9498 | 0.8706 | 0.0850 | 0.8246 | 0.8935 | 0.8577 | 0.6503 | 235/50/28/535 |
| 20260517-143354-recall-low-lr-long | 0.80 | 0.03 | native | neutralized | 0.9501 | 0.8746 | 0.0993 | 0.8264 | 0.8327 | 0.8295 | 0.5769 | 219/46/44/539 |
| 20260517-143457-recall-fast-lr-short | 0.75 | 0.10 | native | neutralized | 0.9491 | 0.8719 | 0.0831 | 0.8252 | 0.7719 | 0.7976 | 0.7780 | 203/43/60/542 |
| 20260517-143526-recall-median-impute | 0.75 | 0.05 | median_impute | neutralized | 0.9493 | 0.8740 | 0.0821 | 0.8308 | 0.8403 | 0.8355 | 0.7315 | 221/45/42/540 |
| 20260517-143619-recall-bpmeds-observed | 0.75 | 0.05 | native | observed | 0.9555 | 0.8890 | 0.0773 | 0.8230 | 0.7605 | 0.7905 | 0.7752 | 200/43/63/542 |

## 二、选择依据

`recall-min85` 在测试集上命中 235 个正样本，只漏报 28 个，高于其他 recall-priority 方案；同时 F1=0.8577 为六组最高。虽然 `bpmeds_observed` 的 AUC 更高，但 Recall=0.7605、F1=0.7905，不适合作为当前“召回优先”的生产模型。

## 三、后续建议

后续如需进一步提升，可以围绕 `recall-min85` 做多 seed 稳定性审计，再决定是否把 `threshold_min_recall=0.85` 固化为长期默认值。
