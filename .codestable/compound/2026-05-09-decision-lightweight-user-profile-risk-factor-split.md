---
doc_type: decision
category: architecture
date: "2026-05-09"
slug: lightweight-user-profile-risk-factor-split
status: active
area: user-profile
tags: [user-profiles, risk-factors, training-data, prediction-inputs]
---

## 背景

普通用户个人档案同时包含展示资料、诊断反馈和进入 7 天风险预测的风险因素。把所有健康字段继续压在 `user_profiles` 中，会让诊断反馈和预测输入边界不清；拆得过细又会让档案结构过散。

## 决定

系统将普通用户个人档案轻量拆分为 `user_profiles` 和 `user_risk_factor_profiles`：前者保存展示资料与诊断反馈，后者保存进入 7 天风险预测的风险因素档案。

## 理由

这个拆分避免诊断反馈被误用为预测输入，并让训练数据导出的标签来源与预测特征来源保持清晰边界；同时没有继续拆出独立诊断反馈表，避免档案结构过散。

## 考虑过的替代方案

- 继续把所有健康字段保存在 `user_profiles`：结构简单，但预测输入和诊断反馈容易混淆。
- 拆出独立诊断反馈表：边界更细，但当前阶段会让档案结构过散。

## 后果

- 预测输入应从 `user_risk_factor_profiles` 读取风险因素档案。
- 展示资料与诊断反馈继续归属于 `user_profiles`。
- 训练数据导出需要保持标签来源与预测特征来源分离。

## 相关文档

- `docs/adr/0006-lightweight-user-profile-risk-factor-split.md`
- `.codestable/architecture/ARCHITECTURE.md`
