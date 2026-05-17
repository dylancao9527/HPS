# 模型训练报告

## 一、模型概要

| 模型 | 用途 | 保存格式 |
|---|---|---|
| Prophet | 按用户历史血压生成未来7天趋势，采用用户级 Prophet 模型持久化与阈值重训 | user_prophet_models + runtime/prophet_models |
| LightGBM | 高血压风险概率分类 | txt (lgbm_model.txt) |

---

## 二、数据集摘要

| 指标 | 数值 |
|---|---|
| 训练 Profile | raw_baseline |
| 主数据集 | Hypertension-risk-model-main.csv |
| 主数据集样本数 | 4240 |
| 主数据集正样本比例 | 31.1% |
| 系统导出样本数 | 0 |
| 系统导出正样本比例 | — |
| 合并后总样本数 | 4240 |
| 正样本数 | 1317 |
| 负样本数 | 2923 |
| 总体正样本比例 | 31.1% |
| 训练集样本数 | 3392 |
| 测试集样本数 | 848 |
| 调参与最终训练池样本数 | 3052 |
| 阈值验证集样本数 | 340 |
| early-stop 训练样本数 | 2746 |
| early-stop 验证样本数 | 306 |
| 最终重训样本数 | 3052 |
| scale_pos_weight | 2.2194 |
| 缺失值策略 | native |

### 缺失值摘要

| 字段 | 缺失数 |
|---|---|
| cigsPerDay | 29 |
| totChol | 50 |
| BMI | 19 |
| heartRate | 1 |
| glucose | 388 |

---

## 三、LightGBM 调参对比

### 性能对比

| 指标 | Baseline | Tuned |
|---|---|---|
| Accuracy | 0.8927 | 0.9080 |
| AUC | 0.9464 | 0.9498 |
| Precision | 0.7756 | 0.8246 |
| Recall | 0.9202 | 0.8935 |
| F1 | 0.8417 | 0.8577 |
| PR-AUC | 0.8688 | 0.8706 |
| Brier Score | 0.0841 | 0.0850 |
| Threshold | 0.49 | 0.65 |
| Best Iteration | 76 | 32 |

### 概率校准

- ECE: `0.0930`
- 校准分桶数: `10`

| Bin | Count | Avg Pred | Avg True |
|---|---|---|---|
| 0 | 393 | 0.1000 | 0.0153 |
| 1 | 75 | 0.1934 | 0.0667 |
| 2 | 31 | 0.2703 | 0.0968 |
| 3 | 23 | 0.3416 | 0.0000 |
| 4 | 8 | 0.4196 | 0.1250 |
| 5 | 6 | 0.4882 | 0.1667 |
| 6 | 9 | 0.5876 | 0.7778 |
| 7 | 49 | 0.6611 | 0.5714 |
| 8 | 108 | 0.7354 | 0.7500 |
| 9 | 146 | 0.8229 | 0.8973 |

### 调优方式

- 调优器：`LightGBMTunerCV`
- 参数策略：`LightGBMTunerCV official stepwise parameter tuning`
- 交叉验证折数：`5`
- 最优 CV AUC：`0.9512`
- 阈值搜索策略：`recall_priority`
- Recall 下限：`0.85`
- 阈值候选数：`209`
- Recall 约束满足：`True`
- 阈值集隔离范围：`before_tuning`
- best_iteration 来源：`early_stop_valid_refit`

### 最优参数

| 参数 | 数值 |
|---|---|
| lambda_l1 | 0.0001927543479357101 |
| lambda_l2 | 0.0026163495796837433 |
| num_leaves | 11 |
| feature_fraction | 0.8 |
| bagging_fraction | 0.9906407300665623 |
| bagging_freq | 7 |
| min_child_samples | 20 |
| max_depth | - |
| min_gain_to_split | - |
| min_sum_hessian_in_leaf | - |
| extra_trees | - |

### 最终测试集混淆矩阵

| 指标 | 数值 |
|---|---|
| TN | 535 |
| FP | 50 |
| FN | 28 |
| TP | 235 |



---

## 四、特征重要性

| 排名 | 特征 | 重要性 (gain) | 占总 gain 比例 |
|---|---|---|---|
| 1 | sysBP | 24158.3 | 74.2% |
| 2 | diaBP | 6348.3 | 19.5% |
| 3 | BMI | 653.5 | 2.0% |
| 4 | age | 581.3 | 1.8% |
| 5 | heartRate | 340.3 | 1.1% |
| 6 | totChol | 200.3 | 0.6% |
| 7 | glucose | 126.0 | 0.4% |
| 8 | cigsPerDay | 103.4 | 0.3% |
| 9 | male | 34.3 | 0.1% |
| 10 | currentSmoker | 0.0 | 0.0% |
| 11 | BPMeds | 0.0 | 0.0% |
| 12 | diabetes | 0.0 | 0.0% |


---

## 五、特征增益解读

- 血压特征总 gain 占比：`93.7%`
- Top3 特征 gain 占比：`95.8%`
- 低信号特征：`totChol, glucose, cigsPerDay, male, currentSmoker, BPMeds, diabetes`

- 当前模型的主要判别信号仍集中在收缩压和舒张压，说明血压水平对分类贡献最强。
- 吸烟和糖尿病特征增益偏低，更可能与样本分布、缺失比例或区分度不足有关，不属于单纯的「梯度没调好」。
- 对树模型而言，通常无需像神经网络那样单独讨论「优化梯度」；更有效的优化方向是特征工程、样本质量、正则化和阈值策略。


---

## 八、训练与更新流程

1. 主训练集使用 `Hypertension-risk-model-main.csv`
2. 管理员可导出 `training_data_export.csv` 作为系统样本补充
3. 运行 `cd backend && uv run python scripts/train_models.py`；如需显式控制随机性，可追加 `--seed <int>` 或 `--random-seed`
4. 脚本自动合并主数据集与系统导出样本，并先拆分测试集和独立阈值验证集
5. LightGBMTunerCV、early stopping 和最终重训只使用阈值集之外的训练池；模型参数冻结后再用独立阈值集搜索分类阈值
6. 默认训练会通过候选产物目录发布到 `backend/ml_models/`，并同步更新唯一的 canonical 报告与模型配置

---

## 九、Prophet 性能优化说明

本项目中的 Prophet 模型持久化在用户维度进行：预测链路会根据新增血压自然日数量判断是否重训，未达到阈值时复用已有模型重新生成本次未来7天血压趋势。为平衡预测效果与交互效率，系统默认仅截取最近 `90` 天的日均血压数据参与训练，并同步返回 `total_history_days` 与 `history_window_capped` 字段说明本次训练窗口情况。
