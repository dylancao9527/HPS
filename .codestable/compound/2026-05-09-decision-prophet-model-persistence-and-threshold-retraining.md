---
doc_type: decision
category: architecture
date: "2026-05-09"
slug: prophet-model-persistence-and-threshold-retraining
status: active
area: prediction
tags: [prophet, model-persistence, retraining, prediction-freshness]
---

## 背景

系统需要在用户预测入口里使用 Prophet 趋势预测，但不能让每次预测都变成昂贵的无条件重训，也不能简单复用旧预测结果而牺牲本次预测记录的新鲜度和可追溯性。

## 决定

系统持久化用户级 Prophet 模型；当新增血压自然日达到配置阈值时重训，否则复用已有 Prophet 模型重新生成本次趋势预测和风险结果。

## 理由

这个做法在交互性能、结果新鲜度和预测记录可追溯性之间取得平衡，同时保留论文中说明模型治理与工程优化的空间。

## 考虑过的替代方案

- 每次预测时无条件重训 Prophet：结果更新直接，但交互性能成本过高。
- 直接复用旧预测结果：性能开销低，但会削弱本次预测记录的新鲜度和追踪价值。

## 后果

- 预测链路需要维护用户级 Prophet 模型资产和重训阈值判断。
- 预测记录仍然代表本次运行结果，而不是旧结果的简单回放。

## 相关文档

- `docs/adr/0001-prophet-model-persistence-and-threshold-retraining.md`
- `.codestable/architecture/ARCHITECTURE.md`
