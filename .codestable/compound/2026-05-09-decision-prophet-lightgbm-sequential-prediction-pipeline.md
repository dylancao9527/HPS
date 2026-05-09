---
doc_type: decision
category: architecture
date: "2026-05-09"
slug: prophet-lightgbm-sequential-prediction-pipeline
status: active
area: prediction
tags: [prophet, lightgbm, prediction-pipeline, risk-scoring]
---

## 背景

系统论文题目固定为“基于Prophet与LightGBM的高血压风险预测系统设计与实现”，预测链路需要同时体现短期血压趋势和用户个人风险因素，而不是只根据最近一次血压做静态分类。

## 决定

系统采用 Prophet 与 LightGBM 串联的双模型预测引擎：先用 Prophet 将用户历史血压记录转换为未来 7 天预测期血压特征，再由 LightGBM 结合用户个人风险因素输出高血压发病风险概率。

## 理由

这个链路把短期血压趋势纳入风险评估，并与论文题目和系统核心叙述保持一致。

## 考虑过的替代方案

- 只基于最近一次血压做静态分类：实现更简单，但无法体现短期趋势对风险评估的作用。

## 后果

- 预测主流程必须维护 Prophet 趋势预测和 LightGBM 风险分类的顺序依赖。
- 训练、评估、论文说明和接口展示都需要围绕双模型链路组织。

## 相关文档

- `docs/adr/0003-prophet-lightgbm-sequential-prediction-pipeline.md`
- `.codestable/architecture/ARCHITECTURE.md`
