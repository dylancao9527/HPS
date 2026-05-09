---
doc_type: decision
category: architecture
date: "2026-05-09"
slug: compact-prediction-record-storage
status: active
supersedes: 2026-05-09-decision-normalized-prediction-result-storage.md
area: prediction-storage
tags: [prediction-records, compact-storage, json-payload, governance]
---

## 背景

用户端预测摘要和预测结果治理仍然需要保存一次 7 天风险预测的趋势、输入快照、风险融合信息、置信度说明和指南型健康建议。但旧方案将这些内容拆成 `prediction_records`、`prophet_predictions`、`prophet_forecast_points`、`prediction_training_meta`、`prediction_input_snapshots`、`prediction_fusion_meta`、`prediction_confidence_reasons` 和 `prediction_recommendations` 八张表，导致数据库结构过散、迁移维护成本偏高。

## 决定

系统改为以 `prediction_records` 作为预测记录聚合表：风险概率、风险等级、数据天数、置信度、运行模式和异常标记保留为可筛选列；血压趋势预测、输入快照、风险融合元信息、Prophet 训练说明、置信度原因和指南型健康建议保存为 JSON 载荷。`user_prophet_models` 继续只负责 Prophet 模型资产持久化，不再承担一次预测历史的明细存储。

## 理由

这个做法降低数据库表数量和迁移维护成本，让预测记录接口更集中，也更符合用户端摘要展示和一期预测结果治理的实际查询需求。

## 考虑过的替代方案

- 继续使用 ADR-0002 的多表规范化预测结果存储：逐字段 SQL 关联查询能力更强，但表数量和维护复杂度偏高。

## 后果

- 牺牲逐字段 SQL 关联查询能力。
- 治理页仍可按风险等级、置信度和是否异常筛选。
- 异常类型基于预测记录载荷投影得到。
- `user_prophet_models` 的职责保持在 Prophet 模型资产持久化，不承载一次预测历史明细。

## 相关文档

- `docs/adr/0007-compact-prediction-record-storage.md`
- `.codestable/compound/2026-05-09-decision-normalized-prediction-result-storage.md`
- `.codestable/architecture/ARCHITECTURE.md`
