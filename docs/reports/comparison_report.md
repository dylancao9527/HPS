# 训练对照实验报告

- Baseline 结果: `D:\projects\HPS\backend\ml_runs\20260516-225844-baseline-recall`
- Experiment 结果: `D:\projects\HPS\backend\ml_runs\20260516-225919-experiment-f1`

## 一、参数差异

| 参数 | Baseline | Experiment |
|---|---|---|
| threshold_min_recall | 0.7500 | — |
| threshold_search_mode | recall_priority | f1 |

## 二、数据集

| 项目 | Baseline | Experiment |
|---|---|---|
| 数据集 | Hypertension-risk-model-main.csv | Hypertension-risk-model-main.csv |
| 样本数 | 4240 | 4240 |
| 正样本比例 | 31.1% | 31.1% |

## 三、Baseline 模型对比

| 指标 | Baseline | Experiment | 差异 |
|---|---:|---:|---|
| AUC | 0.9464 | 0.9464 | +0.0000 ≈ |
| Recall | 0.7338 | 0.9240 | +0.1902 ↑ |
| Precision | 0.8391 | 0.7690 | -0.0701 ↓ |
| F1 | 0.7830 | 0.8394 | +0.0564 ↑ |
| PR-AUC | 0.8688 | 0.8688 | +0.0000 ≈ |
| Brier Score | 0.0841 | 0.0841 | +0.0000 ≈ |
| Accuracy | 0.8738 | 0.8903 | +0.0165 ↑ |
| Threshold | 0.7855 | 0.4651 | -0.3204 ↓ |
| Best Iteration | 76 | 76 | |

## 四、Tuned 模型对比（核心结果）

| 指标 | Baseline | Experiment | 差异 |
|---|---:|---:|---|
| AUC | 0.9480 | 0.9480 | +0.0000 ≈ |
| Recall | 0.7719 | 0.8897 | +0.1178 ↑ |
| Precision | 0.8286 | 0.8125 | -0.0161 ↓ |
| F1 | 0.7992 | 0.8494 | +0.0502 ↑ |
| PR-AUC | 0.8678 | 0.8678 | +0.0000 ≈ |
| Brier Score | 0.0829 | 0.0829 | +0.0000 ≈ |
| Accuracy | 0.8797 | 0.9021 | +0.0224 ↑ |
| Threshold | 0.7732 | 0.6676 | -0.1057 ↓ |
| Best Iteration | 65 | 65 | |

## 五、TunerCV 调参对比

| 项目 | Baseline | Experiment | 差异 |
|---|---:|---:|---|
| CV AUC | 0.9527 | 0.9527 | +0.0000 ≈ |
| Best Iteration | 135 | 135 | |

### 调优参数差异

| 参数 | Baseline | Experiment |
|---|---|---|
| bagging_fraction | 0.9797 | 0.9797 |
| bagging_freq | 7 | 7 |
| feature_fraction | 0.9000 | 0.9000 |
| lambda_l1 | 0.0004 | 0.0004 |
| lambda_l2 | 0.0000 | 0.0000 |
| min_child_samples | 20 | 20 |
| num_leaves | 11 | 11 |

## 六、混淆矩阵对比

| 指标 | Baseline | Experiment |
|---|---:|---:|
| TN | 543 | 531 |
| FP | 42 | 54 |
| FN | 60 | 29 |
| TP | 203 | 234 |

## 七、特征重要性对比

| 特征 | Baseline gain% | Experiment gain% |
|---|---:|---:|
| sysBP | 70.8% | 70.8% |
| diaBP | 18.5% | 18.5% |
| BMI | 3.4% | 3.4% |
| age | 2.2% | 2.2% |
| heartRate | 1.5% | 1.5% |
| glucose | 1.3% | 1.3% |
| totChol | 1.2% | 1.2% |
| cigsPerDay | 0.7% | 0.7% |
| male | 0.4% | 0.4% |
| currentSmoker | 0.0% | 0.0% |
| BPMeds | 0.0% | 0.0% |
| diabetes | 0.0% | 0.0% |
| **血压合计** | **89.4%** | **89.4%** |
