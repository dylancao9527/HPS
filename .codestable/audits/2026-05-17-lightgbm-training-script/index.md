---
doc_type: audit-index
audit: 2026-05-17-lightgbm-training-script
scope: LightGBM training script, training pipeline, data ingestion, threshold search, and model artifact promotion.
created: 2026-05-17
status: fixed
total_findings: 5
---

# lightgbm-training-script 审计报告

## 范围

本次审计范围收敛在 LightGBM 训练脚本与训练链路：`backend/scripts/train_models.py`、`backend/training/config.py`、`backend/training/data.py`、`backend/training/pipeline.py`、`backend/training/trainer.py`、`backend/training/metrics.py`、`backend/training/reporting.py`，并补看线上加载契约 `backend/prediction/infrastructure/model_registry.py` 与 `backend/prediction/infrastructure/risk_model_gateway.py`。架构对照来源为 `.codestable/architecture/ARCHITECTURE.md` 第 13 节的训练与实验说明。

## 总评

共发现 5 条问题：P1 3 条、P2 2 条；性质分布为 bug 3 条、security 1 条、maintainability 1 条。最值得优先处理的是阈值验证集在调参阶段已经参与 CV、阈值搜索候选集无法覆盖最高召回边界，以及默认训练直接覆盖生产模型产物且不是原子替换。整体看，训练链路已经具备固定 seed、命名实验目录、参数快照、训练元信息和报告输出，但在实验隔离、输入约束、配置防错和产物发布安全性上还可以收紧。

## 发现清单

| # | 性质 | 严重度 | 置信度 | 标题 | 文件 |
|---|---|---|---|---|---|
| 1 | bug | P1 | high | 阈值验证集在调参阶段已经参与 CV | [finding-01.md](finding-01.md) |
| 2 | bug | P1 | high | 阈值候选集缺少低于最小分数的召回边界 | [finding-02.md](finding-02.md) |
| 3 | maintainability | P2 | high | 参数 JSON 缺少严格 schema 与取值校验 | [finding-03.md](finding-03.md) |
| 4 | security | P2 | medium | 训练数据缺少二值标签与取值范围约束，存在数据污染入口 | [finding-04.md](finding-04.md) |
| 5 | bug | P1 | medium | 默认训练直接覆盖生产模型且非原子写入 | [finding-05.md](finding-05.md) |

## 按维度分布

| 性质 | P0 | P1 | P2 | 合计 |
|---|---|---|---|---|
| bug | 0 | 3 | 0 | 3 |
| security | 0 | 0 | 1 | 1 |
| performance | 0 | 0 | 0 | 0 |
| maintainability | 0 | 0 | 1 | 1 |
| arch-drift | 0 | 0 | 0 | 0 |
| **合计** | **0** | **3** | **2** | **5** |

## 更好的调整方向

- **先修实验隔离**：把 threshold holdout 在调参前切出来，LightGBMTunerCV 只看 model-selection pool；模型与参数冻结后，再用 threshold holdout 搜索分类阈值。
- **重写阈值搜索边界**：候选阈值使用 score midpoint 或显式加入低于最小预测分数的候选，保证 `recall_priority` 真能达到可达召回上限；保存阈值时同步保存是否满足 recall 约束。
- **严格化参数文件**：拒绝未知字段，校验枚举、类型和范围，例如 `cv_splits >= 2`、`0 < test_size < 1`、`early_stopping_rounds < max_boost_rounds`、`threshold_search_mode in {"recall_priority","f1"}`。
- **增加训练数据质量门禁**：校验 `Risk` 必须为 0/1，二值特征只能是 0/1/缺失，年龄、血压、BMI、心率、血糖等字段有合理范围；生成 invalid-row summary，超过阈值直接中断训练。
- **把模型发布做成两阶段**：默认写入 named run；显式 `--promote` 时先写临时目录、完成 smoke load 和 config/model 一致性校验后，再原子替换生产目录，并保留上一版回滚点。
- **模型效果调优建议**：除 AUC 外并列追踪 PR-AUC、Recall@Precision、Brier/ECE；对于概率展示场景，考虑在独立校准集上做 Platt 或 isotonic calibration，再进入趋势融合。

## 下一步建议

- **P1 本迭代修**：Finding 01、02、05。它们直接影响实验可信度、召回阈值策略和生产模型资产安全。
- **P2 排进训练治理增强**：Finding 03、04。它们不是当前默认数据集必现问题，但会在参数实验、系统导出样本增多或数据源被污染时放大。

## 修复结果

- 5 条发现已全部修复，闭环记录见 [fix-note.md](fix-note.md)。
- 训练链路已将阈值验证集提前切出，LightGBMTunerCV、early stopping 和最终重训均不再使用阈值集。
- 阈值搜索已覆盖最低/最高预测分数外侧边界，并记录 Recall 约束是否满足。
- 参数文件与训练 CSV 已增加入口校验。
- 生产模型发布已改为候选产物目录校验后再替换，并保留上一版备份。
