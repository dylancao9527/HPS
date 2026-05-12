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
| 阈值验证集样本数 | 340 |
| early-stop 训练样本数 | 2746 |
| early-stop 验证样本数 | 306 |
| 最终重训样本数 | 3052 |
| scale_pos_weight | 2.2182 |
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
| Accuracy | 0.8738 | 0.8797 |
| AUC | 0.9464 | 0.9480 |
| Precision | 0.8391 | 0.8286 |
| Recall | 0.7338 | 0.7719 |
| F1 | 0.7830 | 0.7992 |
| PR-AUC | 0.8688 | 0.8678 |
| Brier Score | 0.0841 | 0.0829 |
| Threshold | 0.79 | 0.77 |
| Best Iteration | 76 | 65 |

### 概率校准

- ECE: `0.0674`
- 校准分桶数: `10`

| Bin | Count | Avg Pred | Avg True |
|---|---|---|---|
| 0 | 380 | 0.0482 | 0.0132 |
| 1 | 80 | 0.1515 | 0.0625 |
| 2 | 35 | 0.2472 | 0.0857 |
| 3 | 22 | 0.3452 | 0.0455 |
| 4 | 14 | 0.4373 | 0.0714 |
| 5 | 13 | 0.5353 | 0.4615 |
| 6 | 17 | 0.6304 | 0.4706 |
| 7 | 42 | 0.7315 | 0.7381 |
| 8 | 87 | 0.8237 | 0.7011 |
| 9 | 158 | 0.9288 | 0.8987 |

### 调优方式

- 调优器：`LightGBMTunerCV`
- 参数策略：`LightGBMTunerCV official stepwise parameter tuning`
- 交叉验证折数：`5`
- 最优 CV AUC：`0.9527`
- 阈值搜索策略：`recall_priority`
- Recall 下限：`0.75`
- 阈值候选数：`298`
- 阈值集与 early stopping 隔离：`True`
- best_iteration 来源：`early_stop_valid_refit`

### 最优参数

| 参数 | 数值 |
|---|---|
| lambda_l1 | 0.00042666326293872416 |
| lambda_l2 | 1.544395967913497e-07 |
| num_leaves | 11 |
| feature_fraction | 0.8999999999999999 |
| bagging_fraction | 0.979742058775629 |
| bagging_freq | 7 |
| min_child_samples | 20 |
| max_depth | - |
| min_gain_to_split | - |
| min_sum_hessian_in_leaf | - |
| extra_trees | - |

### 最终测试集混淆矩阵

| 指标 | 数值 |
|---|---|
| TN | 543 |
| FP | 42 |
| FN | 60 |
| TP | 203 |



---

## 四、特征重要性

| 排名 | 特征 | 重要性 (gain) | 占总 gain 比例 |
|---|---|---|---|
| 1 | sysBP | 26513.8 | 70.8% |
| 2 | diaBP | 6938.2 | 18.5% |
| 3 | BMI | 1280.8 | 3.4% |
| 4 | age | 810.8 | 2.2% |
| 5 | heartRate | 575.1 | 1.5% |
| 6 | glucose | 477.0 | 1.3% |
| 7 | totChol | 444.3 | 1.2% |
| 8 | cigsPerDay | 255.8 | 0.7% |
| 9 | male | 136.5 | 0.4% |
| 10 | currentSmoker | 0.0 | 0.0% |
| 11 | BPMeds | 0.0 | 0.0% |
| 12 | diabetes | 0.0 | 0.0% |


---

## 五、特征增益解读

- 血压特征总 gain 占比：`89.4%`
- Top3 特征 gain 占比：`92.8%`
- 低信号特征：`cigsPerDay, male, currentSmoker, BPMeds, diabetes`

- 当前模型的主要判别信号仍集中在收缩压和舒张压，说明血压水平对分类贡献最强。
- 吸烟和糖尿病特征增益偏低，更可能与样本分布、缺失比例或区分度不足有关，不属于单纯的「梯度没调好」。
- 对树模型而言，通常无需像神经网络那样单独讨论「优化梯度」；更有效的优化方向是特征工程、样本质量、正则化和阈值策略。


---

## 八、训练与更新流程

1. 主训练集使用 `Hypertension-risk-model-main.csv`
2. 管理员可导出 `training_data_export.csv` 作为系统样本补充
3. 运行 `cd backend && uv run python scripts/train_models.py`；如需显式控制随机性，可追加 `--seed <int>` 或 `--random-seed`
4. 脚本自动合并主数据集与系统导出样本，并拆分出测试集、阈值验证集和 early-stopping 验证集
5. 先在 early-stopping 验证集上确定最佳迭代轮数，再用完整训练池重训最终模型，并在独立阈值集上搜索分类阈值
6. 默认训练会覆盖 `backend/ml_models/` 下的生产文件，并同步更新唯一的 canonical 报告与模型配置

---

## 九、Prophet 性能优化说明

本项目中的 Prophet 模型持久化在用户维度进行：预测链路会根据新增血压自然日数量判断是否重训，未达到阈值时复用已有模型重新生成本次未来7天血压趋势。为平衡预测效果与交互效率，系统默认仅截取最近 `90` 天的日均血压数据参与训练，并同步返回 `total_history_days` 与 `history_window_capped` 字段说明本次训练窗口情况。
