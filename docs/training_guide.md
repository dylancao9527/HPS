# LightGBM 训练参数与评估指标说明

## 一、评估指标

### 1.1 基础概念：混淆矩阵

模型对每个样本预测"高风险"或"低风险"，与真实标签对比产生四种情况：

|  | **预测：高风险** | **预测：低风险** |
|---|---|---|
| **实际：高风险** | TP（真正例） ✅ | FN（漏报） ❌ |
| **实际：低风险** | FP（误报） ❌ | TN（真负例） ✅ |

当前模型在 framingham 测试集上的结果：TP=203, FP=42, FN=60, TN=543

### 1.2 核心指标

| 指标 | 公式 | 含义 | 当前值 | 通俗理解 |
|---|---|---|---:|---|
| **Accuracy** | (TP+TN) / 总数 | 整体预测正确率 | 0.8797 | 848 个样本中，约 746 个预测正确 |
| **Precision** | TP / (TP+FP) | 预测为高风险的样本中，真正高风险的比例 | 0.8286 | 模型说"高风险"的 245 人中，203 人确实高风险 |
| **Recall** | TP / (TP+FN) | 所有真正高风险的样本中，被模型找出来的比例 | 0.7719 | 263 个真实高风险者中，模型找出了 203 个 |
| **F1** | 2×P×R / (P+R) | Precision 和 Recall 的调和平均 | 0.7992 | 综合反映查准和查全的平衡 |
| **AUC** | ROC 曲线下面积 | 模型区分正负样本的整体能力（不受阈值影响） | 0.9480 | 1.0 是完美，0.5 是随机猜；0.95 属于很强 |
| **PR-AUC** | PR 曲线下面积 | 在不同阈值下 Precision-Recall 的综合表现 | 0.8678 | 比 AUC 对正样本少的数据更敏感 |
| **Brier Score** | 均方概率误差 | 预测概率与真实标签的偏差 | 0.0829 | 越小越好，0 是完美 |

### 1.3 Precision 和 Recall 的权衡

Precision 和 Recall 是一对矛盾：

- **提高 Precision**（降低阈值门槛要求）→ 减少误报，但会漏掉更多高风险者
- **提高 Recall**（降低分类阈值）→ 找出更多高风险者，但误报也增多

本系统面向普通用户健康参考，采用 **recall_priority** 策略，设置 Recall 下限 0.75，意思是：宁可多报一些假阳性，也不要漏掉太多真正高风险的人。

### 1.4 阈值（Threshold）的作用

LightGBM 输出的是一个 0~1 的**概率值**。阈值决定多高的概率算"高风险"：

```
概率 ≥ 阈值 → 预测为高风险
概率 < 阈值 → 预测为低风险
```

当前阈值 **0.77** 表示：模型输出概率 ≥ 77% 才会被判定为高风险。阈值越高，判定越严格（Precision↑ Recall↓）；越低越宽松（Precision↓ Recall↑）。

### 1.5 AUC 与 Brier Score

- **AUC** 衡量的是排序能力：给一个高风险和一个低风险样本，模型给高风险者更高概率的可能性。AUC=0.95 意味着 95% 的情况下模型能正确排序
- **Brier Score** 衡量的是概率校准：模型说 80% 概率的样本群体中，是否真的约有 80% 是高风险。越小越准

---

## 二、训练参数说明

### 2.1 数据划分参数

| 参数 | 默认值 | 作用 |
|---|---:|---|
| `seed` | 42 | 随机种子。固定 seed 保证每次训练结果完全一致；换 seed 可验证模型稳定性 |
| `test_size` | 0.2 | 测试集占比。4240 样本 × 0.2 = 848 行用于最终评估，不参与训练 |
| `threshold_valid_size` | 0.1 | 阈值搜索专用验证集占比。从训练集中再隔离 10% 专门用来搜索最优阈值，避免阈值对训练数据过拟合 |
| `cv_splits` | 5 | TunerCV 交叉验证折数。5 折意味着数据分 5 份，轮流用 4 份训练 1 份验证 |

**数据流向**：

```
4240 样本
├── 测试集 848 (20%) ← 最终评估，完全隔离
└── 训练集 3392 (80%)
    ├── 阈值验证集 340 (10%) ← 搜索最优分类阈值
    └── 模型训练池 3052 (90%)
        ├── early-stop 训练 2746
        └── early-stop 验证 306
```

### 2.2 训练控制参数

| 参数 | 默认值 | 作用 | 调整建议 |
|---|---:|---|---|
| `learning_rate` | 0.05 | 每棵树的学习步长 | 调小（如 0.03）→ 更精细但更慢；调大（如 0.1）→ 更快但易过拟合 |
| `max_boost_rounds` | 1000 | 最多训练多少棵树 | 通常不需要改，early_stopping 会提前截断 |
| `early_stopping_rounds` | 50 | 验证集连续 N 轮不提升就停训 | 调大（如 100）→ 等更久，小数据集上可能过拟合；调小（如 30）→ 停得更快 |

**三者的关系**：`learning_rate` 越小，需要的树越多（`max_boost_rounds` 要够大），`early_stopping_rounds` 也要适当加大以等待缓慢的收敛。

### 2.3 阈值搜索参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `threshold_search_mode` | `recall_priority` | 搜索策略。`recall_priority` 先保证 Recall 不低于下限，再选 F1 最高的阈值；`f1` 则直接选 F1 最高的阈值不设 Recall 下限 |
| `threshold_min_recall` | 0.75 | Recall 下限约束。只在 `recall_priority` 模式下生效 |

**效果示例**：

| min_recall | 预期效果 |
|---:|---|
| 0.6 | 阈值很高，Precision 高但漏掉 40% 高风险者 |
| **0.75** | 当前设置，平衡点 |
| 0.8 | 阈值降低，少漏人但误报增多 |
| 0.9 | 几乎不漏人，但很多低风险者也会被标为高风险 |

### 2.4 数据处理参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `missing_value_strategy` | `native` | 缺失值处理。`native` = LightGBM 内置处理（自动找最优分裂方向）；`median_impute` = 用中位数填充 |
| `bp_meds_policy` | `neutralized_for_conservative_inference` | 降压药特征处理。`neutralized` = 将 BPMeds 字段置 0，避免"正在服药"被模型误判为高风险信号；`observed` = 保留原始值 |
| `label_mode` | `diagnosis_plus_rule` | 标签来源。`diagnosis_plus_rule` = 使用数据集原始 Risk 列 + 补充规则；`diagnosis_only` = 只用原始 Risk 列 |

### 2.5 实验扩展参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `enable_feature_ablation` | false | 特征消融实验。`true` 时会额外训练多组特征子集，对比哪些特征组合效果最好 |
| `multi_seed_audit_seeds` | [] | 多 seed 稳定性审计。填入多个 seed（如 `[42, 123, 456]`）后会跑多轮训练并统计 AUC 均值和标准差，验证模型是否对数据划分敏感 |

---

## 三、LightGBMTunerCV 调参过程

LightGBMTunerCV 采用**逐步贪心搜索**，按以下顺序依次调优 6 组参数：

| 步骤 | 搜索参数 | 搜索内容 | 为什么这个顺序 |
|---|---|---|---|
| ① | `feature_fraction` | 每棵树用多少比例的特征列 | 先控制特征采样范围 |
| ② | `num_leaves` | 每棵树最多多少个叶子节点 | 确定树的复杂度 |
| ③ | `bagging_fraction` + `bagging_freq` | 每轮训练用多少比例的样本行，多少轮做一次采样 | 在树结构确定后控制样本采样 |
| ④ | `feature_fraction` (stage2) | 在①基础上更精细搜索特征比例 | 微调 |
| ⑤ | `lambda_l1` + `lambda_l2` | L1 正则化（稀疏化）和 L2 正则化（平滑化） | 在模型结构确定后加正则防过拟合 |
| ⑥ | `min_child_samples` | 叶子节点最少需要多少样本才能分裂 | 最后控制叶子的样本量门槛 |

每一步用 5-fold CV 评估 AUC，`val_score` 就是当前步搜到的最优 CV AUC。进度条右侧的数字表示该步搜索了多少个候选值。

---

## 四、如何判断模型更好

### 4.1 指标优先级

对比两组参数的训练结果时，按以下优先级判断：

| 优先级 | 指标 | 判断标准 | 原因 |
|---:|---|---|---|
| ① | **AUC** | 越高越好，≥0.94 算强 | 不受阈值影响，反映模型本身的区分能力 |
| ② | **Brier Score** | 越小越好，≤0.10 算健康 | 反映概率输出质量，太大说明模型概率不可信 |
| ③ | **F1** | 越高越好 | 综合 Precision 和 Recall 的平衡 |
| ④ | **Threshold** | 应在 0.4~0.8 之间 | 太低说明模型概率分布有问题 |
| ⑤ | **CV AUC vs 测试 AUC** | 差距越小越好 | 差距大说明过拟合 |

### 4.2 常见陷阱

| 现象 | 诊断 | 示例 |
|---|---|---|
| Recall 很高但 Threshold 很低（<0.4） | 模型概率分布偏移，不是真的更好 | lr=0.003 那次：Recall=0.85 但 Threshold=0.34、Brier=0.20 |
| AUC 高但 F1 低 | 阈值选得不好，或正负样本极度不平衡 | — |
| CV AUC 比测试 AUC 高很多 | 过拟合，训练集学到了噪声 | num_leaves=244 时容易出现 |
| Best Iteration 很小（<30） | 模型还没学够就停了 | early_stopping_rounds 设太小 |
| Best Iteration 接近 max_boost_rounds | 可能还没收敛，需要加大 max_boost_rounds | — |

### 4.3 快速判断清单

拿到两组结果后，按顺序检查：

1. **AUC 谁高？** — 区分能力更强的胜出
2. **Brier Score 谁低？** — 概率更可信的胜出。如果一方 Brier 翻倍（如 0.08 vs 0.20），即使 F1 更高也不可取
3. **Threshold 是否合理？** — 如果 < 0.4，说明模型的概率分布有问题，高 Recall 是假象
4. **CV AUC 和测试 AUC 差多少？** — 差距 > 0.01 要警惕过拟合
5. **F1 谁高？** — 在以上都通过的前提下，F1 高的更好

### 4.4 指标速查表

| 指标 | 好的范围 | 方向 | 一句话 |
|---|---|---|---|
| AUC | ≥ 0.94 | 越高越好 | 模型能区分高低风险的能力 |
| Brier Score | ≤ 0.10 | 越小越好 | 模型概率输出的准确程度 |
| F1 | ≥ 0.78 | 越高越好 | 查准和查全的综合分数 |
| Precision | ≥ 0.80 | 越高越好 | 模型说"高风险"有多可信 |
| Recall | ≥ 0.75 | 越高越好 | 高风险者被找出来的比例 |
| PR-AUC | ≥ 0.85 | 越高越好 | 在正样本少时比 AUC 更敏感 |
| Threshold | 0.4 ~ 0.8 | 合理即可 | 太低说明概率分布有问题 |
| Accuracy | ≥ 0.87 | 越高越好 | 整体正确率（正负样本不平衡时参考价值有限） |

---

## 五、参数速查表

| 参数 | 默认值 | 含义 | 调大 | 调小 |
|---|---|---|---|---|
| `seed` | 42 | 随机种子 | 换值验证稳定性 | — |
| `test_size` | 0.2 | 测试集占比 | 测试更充分，训练数据更少 | 训练更充分，测试可能不稳 |
| `threshold_valid_size` | 0.1 | 阈值验证集占比 | 阈值搜索更稳定 | 训练数据更多 |
| `cv_splits` | 5 | CV 折数 | 评估更稳但更慢 | 更快但波动大 |
| `early_stopping_rounds` | 50 | 连续无提升停训轮数 | 等更久，可能过拟合 | 停太早，欠拟合 |
| `max_boost_rounds` | 1000 | 最大树数量 | 允许更长训练 | 可能截断过早 |
| `threshold_search_mode` | `recall_priority` | 阈值策略 | — | 换 `f1` 不设 Recall 下限 |
| `threshold_min_recall` | 0.75 | Recall 下限 | 少漏人但多误报 | 少误报但漏更多人 |
| `missing_value_strategy` | `native` | 缺失值处理 | — | 换 `median_impute` 用中位数填 |
| `learning_rate` | 0.05 | 学习步长 | 收敛快但易过拟合 | 更精细但需要更多轮 |
| `bp_meds_policy` | `neutralized_...` | 降压药字段 | — | 换 `observed` 用原始值 |
| `label_mode` | `diagnosis_plus_rule` | 标签来源 | — | 换 `diagnosis_only` 只用原始标签 |
| `enable_feature_ablation` | false | 特征消融 | `true` 跑多组特征子集对比 | — |
| `multi_seed_audit_seeds` | [] | 多 seed 审计 | 填多个 seed 验证稳定性 | — |

---

## 六、对照实验操作流程

### 6.1 操作步骤

```bash
cd backend

# 1. 编辑参数文件
#    scripts/experiments/baseline.json   ← 对照组
#    scripts/experiments/experiment.json  ← 实验组

# 2. 跑 baseline，保存结果
uv run python scripts/train_models.py --params scripts/experiments/baseline.json
copy ml_models\training_meta.json scripts\experiments\baseline_result.json

# 3. 跑 experiment，保存结果
uv run python scripts/train_models.py --params scripts/experiments/experiment.json
copy ml_models\training_meta.json scripts\experiments\experiment_result.json

# 4. 生成对比报告
uv run python scripts/experiments/compare.py --output ../docs/reports/comparison_report.md
```

### 6.2 对比报告说明

`compare.py` 会自动读取两个 `_result.json`，输出包含以下内容的 Markdown 报告：

| 报告章节 | 内容 |
|---|---|
| 参数差异 | 两组参数中有差异的字段对比 |
| 数据集 | 数据集名称、样本数、正样本比例 |
| Baseline 模型对比 | 未调参模型的指标差异 |
| Tuned 模型对比 | 调参后模型的核心指标差异（最重要） |
| TunerCV 调参对比 | CV AUC 和调优后参数差异 |
| 混淆矩阵 | TP/FP/FN/TN 对比 |
| 特征重要性 | 各特征 gain% 对比 |
