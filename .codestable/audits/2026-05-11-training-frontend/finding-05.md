---
doc_type: audit-finding
audit: 2026-05-11-training-frontend
finding_id: "maintainability-05"
nature: maintainability
severity: P2
confidence: high
suggested_action: cs-refactor
status: fixed
---

# Finding 05：ProfileFormContent 聚合四类表单和密码流程，维护成本偏高

## 速答

`ProfileFormContent` 单个组件约 300 行，同时管理账号、风险因素、诊断反馈、旧密码修改、邮箱验证码重置密码和本地模拟验证码展示，后续改动容易互相牵连。

## 关键证据

- `frontend/src/features/profile/components/ProfileForm.tsx:71` — `ProfileFormContent` 从这一行开始，文件总长 371 行，函数主体延续到文件末尾。
- `frontend/src/features/profile/components/ProfileForm.tsx:76` — 同一组件同时创建 account / health / feedback 三组业务表单状态。
- `frontend/src/features/profile/components/ProfileForm.tsx:83` — 同一组件继续管理密码模式和密码表单状态。
- `frontend/src/features/profile/components/ProfileForm.tsx:225` — 旧密码修改流程在同一组件中实现。
- `frontend/src/features/profile/components/ProfileForm.tsx:255` — 邮箱重置密码发送验证码流程也在同一组件中实现。
- `frontend/src/features/profile/components/ProfileForm.tsx:322` — render 阶段把四个 section 的大量 props 全部从同一组件向下分发。

## 影响

目前功能能工作，但组件已经超过审计阈值（> 80 行）很多，且业务状态、异步请求、表单校验、UI 分发混在一起。后续调整风险因素字段、邮箱变更流程或密码重置流程时，容易引入无关回归，也会让单元测试难以聚焦。

## 修复方向

按 section 拆出 `useAccountProfileSection`、`useHealthProfileSection`、`useProfileFeedbackSection`、`usePasswordSettingsSection` 等 hook，`ProfileFormContent` 只负责选择 section 与组合布局。

## 建议动作

`cs-refactor`，因为这是行为不变的结构整理，适合小步拆分并用现有 profile tests 兜底。
