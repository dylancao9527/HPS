# 论文补强发现记录

## 已有材料

- `lunwen-doc/基于Prophet与LightGBM的高血压风险预测系统设计与实现.md` 和 `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现.md` 已存在。
- 已有主论文 DOCX、附件 DOCX、参考文献池、参考文献核验清单。
- 已有页面截图 6 张：风险因素档案、血压记录、风险预测、预测结果、预测历史、预测结果治理。
- 已有图表 5 组：Prophet 流程、LightGBM 输入输出、双模型链路、预测治理流程、核心 E-R 图。

## 当前论文已经覆盖的内容

- 第 4 章已经有 Prophet、LightGBM、双模型链路、融合公式、核心数据结构、页面截图等内容。
- 第 5 章已经有 LightGBM 调参对比、阈值策略对照实验、特征重要性、Prophet 回测、趋势融合效果分析。
- `docs/training_guide.md` 详细说明了 Precision、Recall、F1、AUC、PR-AUC、Brier Score、阈值策略和 LightGBMTunerCV 调参过程。
- `docs/reports/model_report.md` 提供 Baseline / Tuned 对比、最优 CV AUC、特征重要性和 Prophet 性能优化说明。
- `docs/reports/comparison_report.md` 提供 recall_priority 与 f1 阈值策略对照结果。
- `docs/reports/prophet_evaluation_report.md` 提供 Prophet cross_validation 回测方法和不同 profile 结果。
- `docs/reports/trend_fusion_report.md` 提供趋势融合场景评价结果。

## 需要补强的方向

- 第 2 章或第 4 章需要更系统地介绍 Prophet 与 LightGBM 的核心公式和方法原理。
- 第 4 章需要把“Prophet 预测期血压特征 → LightGBM 风险概率 → 趋势融合概率”的链路写得更像模型设计，而不是只像系统流程。
- 第 5 章需要更明确解释：调参不是让所有指标都暴涨，而是在高 AUC 基础上提升 Recall、F1 和概率校准，同时保持 Precision 可接受。
- Prophet 需要说明使用加性时间序列模型、趋势项、季节项/节假日项思想，以及本项目为什么选择用户级训练、90 天窗口、阈值重训和 profile 参数画像。
- 趋势融合要强调是工程层微调，不替代 LightGBM 主模型，不把规则说成临床风险模型。
- E-R 图需要改成实体 E-R 图表达，而不是只列数据表字段。

## 可直接使用的数据

### 2026-05-10 重新训练结果

- 数据集：`framingham.csv`，样本数 4240，正样本 1317，负样本 2923，正样本比例 31.1%。
- 数据划分：训练集 3392，测试集 848，阈值验证集 340，early-stop 训练集 2746，early-stop 验证集 306，最终重训集 3052。
- 缺失值：`cigsPerDay` 29、`totChol` 50、`BMI` 19、`heartRate` 1、`glucose` 388。
- 最终 Tuned（`f1` 阈值策略）：AUC 0.9480、Accuracy 0.9021、Precision 0.8125、Recall 0.8897、F1 0.8494、PR-AUC 0.8678、Brier Score 0.0829、Threshold 0.6676。
- 对照 Baseline（同为 `f1` 阈值策略）：AUC 0.9464、Accuracy 0.8903、Precision 0.7690、Recall 0.9240、F1 0.8394、PR-AUC 0.8688、Brier Score 0.0841、Threshold 0.4651。
- Tuned 混淆矩阵（`f1`）：TN 531、FP 54、FN 29、TP 234。
- 调参参数：`num_leaves=11`、`feature_fraction=0.9000`、`bagging_fraction=0.9797`、`bagging_freq=7`、`min_child_samples=20`、`scale_pos_weight=2.2182`，并引入 `lambda_l1`/`lambda_l2`。
- 阈值策略对照：`recall_priority` 的 Tuned 结果为 Precision 0.8286、Recall 0.7719、F1 0.7992、Threshold 0.7732；`f1` 策略为 Precision 0.8125、Recall 0.8897、F1 0.8494、Threshold 0.6676。论文口径：最终采用 `f1`，`recall_priority` 作为更保守对照。
- 特征重要性：`sysBP` 与 `diaBP` 合计约 89.4% gain，支撑 Prophet 预测期血压特征进入 LightGBM。
- Prophet 回测：稳定 profile 在 30 天以上历史数据下 7 天收缩压 MAE 约 3-7 mmHg，高波动 profile 误差更高，支撑低置信度策略。
- 趋势融合：调整幅度控制在约 `[0, +0.12]`，定位为微调。

## 图片与截图判断

- 当前截图基本覆盖第 4 章用户端与管理员端主路径。
- 如果 UI 最近有较大视觉改版，需要重新截图；如果没有，当前截图可以继续使用。
- 需要新绘图的优先级：实体 E-R 图最高，其次是公式化双模型链路图、LightGBM 调参流程图、Prophet 回测设计图。
