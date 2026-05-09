---
doc_type: decision
category: constraint
date: "2026-05-09"
slug: fixed-seven-day-user-prediction
status: active
area: prediction
tags: [prediction-period, user-facing, api-contract]
---

## 背景

普通用户预测入口需要提供易理解的风险预测摘要。多预测周期会增加普通用户理解成本，也会让论文叙述、前端展示和后端接口契约变得分散。

## 决定

普通用户预测入口固定为未来 7 天风险预测，不再提供 3 天或 14 天周期选择；后端预测接口拒绝非 7 天预测周期，数据库中的预测周期字段也约束为 7。

## 理由

这个约束降低普通用户理解成本，保持论文叙述与领域语言一致，并让用户端预测摘要更清晰。

## 考虑过的替代方案

- 继续提供 3 天、7 天、14 天等多周期选择：更灵活，但会增加用户端解释和链路治理成本。

## 后果

- 用户侧预测周期是硬约束，接口和数据库都应拒绝非 7 天周期。
- 输入快照、融合元数据、置信度原因和模型运行细节保留在管理员预测结果治理中查看，不暴露为普通用户周期选择。

## 相关文档

- `docs/adr/0004-fixed-seven-day-user-prediction.md`
- `.codestable/architecture/ARCHITECTURE.md`
