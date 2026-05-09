---
doc_type: decision
category: architecture
date: "2026-05-09"
slug: separate-admin-accounts-from-user-health-profiles
status: active
area: accounts
tags: [admin-users, user-profiles, data-boundary, authorization]
---

## 背景

管理员账号承担后台治理职责，但普通用户表和健康档案承载个人档案、风险因素、诊断反馈、血压记录与预测记录。继续用普通用户表里的角色字段区分账号类型，会模糊后台治理角色和普通用户健康数据之间的边界。

## 决定

系统将管理员账号保存在独立的 `admin_users` 表中，而不是继续通过 `users.role` 在普通用户表中区分角色。

## 理由

独立管理员账号表让数据边界更清晰：管理员只拥有账户信息，不关联个人档案、风险因素档案、诊断反馈、血压记录或预测记录，避免后台治理角色被误纳入普通用户健康数据和预测链路。

## 考虑过的替代方案

- 继续使用 `users.role` 的单表账号模型：实现更简单，但普通用户健康数据边界不够清晰。

## 后果

- 管理员认证、权限判断和账号管理需要面向 `admin_users` 建模。
- 普通用户健康档案与预测链路不应依赖管理员账号数据。

## 相关文档

- `docs/adr/0005-separate-admin-accounts-from-user-health-profiles.md`
- `.codestable/architecture/ARCHITECTURE.md`
