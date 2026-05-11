# 《基于Prophet与LightGBM的高血压风险预测系统设计与实现》术语公式算法沉淀

## 1. 文档用途

本文档用于沉淀论文写作中需要统一的术语、公式、算法流程和双模型联合口径。后续修改正文、制作答辩材料或生成附件时，以本文档中的表述为准。

## 2. 核心术语表

| 术语 | 英文/符号 | 论文统一解释 | 使用边界 |
|---|---|---|---|
| 高血压风险预测 | hypertension risk prediction | 基于用户风险因素和预测期血压特征输出高血压风险概率 | 不写成医学确诊 |
| 血压时间序列 | blood pressure time series | 按时间排列的收缩压、舒张压和心率记录 | 原始记录需先按自然日聚合 |
| 收缩压 | SBP / sysBP | 心脏收缩时动脉压力，LightGBM 中使用 `sysBP` 字段 | 系统预测时来自 Prophet 未来 7 天均值 |
| 舒张压 | DBP / diaBP | 心脏舒张时动脉压力，LightGBM 中使用 `diaBP` 字段 | 系统预测时来自 Prophet 未来 7 天均值 |
| 预测期血压特征 | future blood pressure features | Prophet 生成的未来 7 天收缩压和舒张压预测均值 | 是两个模型的关键衔接点 |
| Prophet 模型 | Prophet | 加性时间序列预测模型，用于预测未来 7 天血压趋势 | 不直接输出高血压风险 |
| LightGBM 模型 | LightGBM | 梯度提升决策树模型，用于结构化风险分类 | 输出原始风险概率 |
| 原始风险概率 | `p_raw` | LightGBM 直接输出的高血压风险概率 | 进入趋势融合前的概率 |
| 融合风险概率 | `p_fused` | 在 `p_raw` 基础上结合趋势信号小幅修正后的概率 | 最终页面展示使用 |
| 趋势融合 | trend fusion | 根据高血压天数、峰值、上升趋势和用药信号调整概率 | 是工程修正，不是第二个分类模型 |
| 置信度说明 | confidence explanation | 对记录长度、波动情况、模型运行模式的解释 | 用于辅助用户理解，不作为医学判断 |
| 健康建议 | guideline-based suggestion | 结合风险等级和血压趋势生成的管理建议 | 不写处方、诊断或治疗方案 |

## 3. 模型输入输出口径

### 3.1 Prophet 输入输出

输入：

- 用户历史血压记录。
- 每条记录包含收缩压、舒张压、心率和记录时间。
- 同一自然日多条记录先聚合为日均收缩压和日均舒张压。

输出：

- 未来 7 天收缩压预测值。
- 未来 7 天舒张压预测值。
- 预测期均值、峰值、高血压天数比例、趋势方向和置信度说明。

### 3.2 LightGBM 输入输出

输入：

- 性别、年龄、是否吸烟、日吸烟支数、是否服用降压药、是否糖尿病、总胆固醇、BMI、心率、血糖。
- Prophet 输出的未来 7 天收缩压均值和舒张压均值，分别映射到 `sysBP` 和 `diaBP`。

输出：

- 原始风险概率 `p_raw`。
- 按阈值映射得到的低风险、中风险和高风险等级。

### 3.3 双模型关系

两个模型是串联关系，不是投票关系：

1. Prophet 先把历史血压记录转换为未来 7 天预测期血压特征。
2. LightGBM 再把预测期血压特征与个人风险因素组合，输出原始风险概率。
3. 趋势融合模块在原始概率上做小幅修正，生成最终展示概率。

## 4. 公式清单

### 4.1 Prophet 加性模型

```text
y(t)=g(t)+s(t)+h(t)+epsilon_t
```

含义：

- `g(t)`：趋势项，用于描述血压序列整体变化方向。
- `s(t)`：周期项，用于描述周期性波动。
- `h(t)`：节假日或事件项，本文不作为主要因素。
- `epsilon_t`：随机误差项。

### 4.2 Prophet 分段趋势项

```text
g(t)=(k+a(t)^T delta)t+(m+a(t)^T gamma)
```

含义：

- `k`：基础增长率。
- `m`：偏置项。
- `a(t)`：变化点指示向量。
- `delta`：变化点前后趋势斜率调整量。
- `gamma`：保证趋势连续的修正项。

### 4.3 日均血压聚合

```text
SBP_bar_d = (1 / n_d) * sum_i SBP_{d,i}
DBP_bar_d = (1 / n_d) * sum_i DBP_{d,i}
```

含义：

- `n_d`：第 `d` 天的血压记录数。
- `SBP_bar_d`、`DBP_bar_d`：第 `d` 天的日均收缩压和日均舒张压。

### 4.4 预测期血压特征

```text
SBP_future = (1 / 7) * sum_{k=1}^{7} SBP_hat_{t+k}
DBP_future = (1 / 7) * sum_{k=1}^{7} DBP_hat_{t+k}
```

含义：

- `SBP_future`、`DBP_future`：输入 LightGBM 的预测期血压均值。
- `SBP_hat_{t+k}`、`DBP_hat_{t+k}`：Prophet 对未来第 `k` 天的预测值。

### 4.5 LightGBM 加法模型

```text
F_M(x)=sum_{m=1}^{M} f_m(x)
```

含义：

- `f_m(x)`：第 `m` 棵树。
- `M`：树的数量。
- `F_M(x)`：多棵树累加后的模型输出。

### 4.6 LightGBM 目标函数

```text
L^(m)=sum_i l(y_i, y_hat_i^(m-1)+f_m(x_i)) + Omega(f_m)
```

含义：

- `l`：样本损失函数。
- `Omega(f_m)`：模型复杂度惩罚。
- 该式说明 LightGBM 每一轮都在已有模型基础上加入新树。

### 4.7 二分类概率输出

```text
p = 1 / (1 + exp(-F_M(x)))
```

含义：

- `p`：样本属于高风险类别的概率。
- 本文中该概率先记为 `p_raw`。

### 4.8 预测期高血压天数比例

```text
r_high = (1 / 7) * sum_{k=1}^{7} I(SBP_hat_{t+k} >= 140 or DBP_hat_{t+k} >= 90)
```

含义：

- `r_high`：未来 7 天中达到高血压阈值的天数比例。
- 该指标进入趋势融合模块。

### 4.9 趋势融合概率

```text
p_fused = clip(p_raw + Delta_trend + Delta_med, 0.01, 0.99)
```

含义：

- `p_raw`：LightGBM 原始风险概率。
- `Delta_trend`：趋势信号调整量。
- `Delta_med`：服药但血压仍偏高时的保守修正量。
- `clip`：将概率约束在合理范围内。

## 5. 双模型联合算法

### 5.1 算法输入

- 用户风险因素档案 `X_risk`。
- 用户历史血压记录 `BP_history`。
- 已训练或可加载的 LightGBM 风险分类模型。

### 5.2 算法输出

- 未来 7 天血压趋势。
- 原始风险概率 `p_raw`。
- 融合风险概率 `p_fused`。
- 风险等级。
- 健康管理建议。

### 5.3 联合算法步骤

```text
Algorithm: Prophet-LightGBM 双模型高血压风险预测

Input:
  BP_history, X_risk, LightGBM_model

Output:
  forecast_points, p_raw, p_fused, risk_level, suggestions

Steps:
  1. 按自然日聚合 BP_history，得到日均收缩压序列和日均舒张压序列。
  2. 使用 Prophet 对日均收缩压序列预测未来 7 天收缩压。
  3. 使用 Prophet 对日均舒张压序列预测未来 7 天舒张压。
  4. 计算未来 7 天预测收缩压均值 SBP_future 和预测舒张压均值 DBP_future。
  5. 将 SBP_future、DBP_future 与 X_risk 合并，形成 LightGBM 输入向量。
  6. 调用 LightGBM_model 得到原始风险概率 p_raw。
  7. 从 forecast_points 中提取高血压天数比例、血压峰值、趋势方向和波动信号。
  8. 根据趋势融合规则计算 Delta_trend 和 Delta_med。
  9. 计算 p_fused，并将其映射为低风险、中风险或高风险。
  10. 根据风险等级、预测趋势和指南规则生成健康管理建议。
```

## 6. 论文写作统一话术

- Prophet 的价值不是替代临床血压预测，而是将历史血压记录转换为可解释的未来 7 天趋势特征。
- LightGBM 的价值在于处理结构化健康风险因素，并输出可用于风险提示的概率。
- 两个模型的关键连接点是预测期血压均值，即 `SBP_future` 和 `DBP_future`。
- 趋势融合是受约束的小幅修正，用于增强结果解释性，不替代 LightGBM。
- 页面展示只用于证明算法链路可运行，不作为论文主要贡献展开。
