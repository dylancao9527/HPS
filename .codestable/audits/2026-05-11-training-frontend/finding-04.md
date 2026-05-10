---
doc_type: audit-finding
audit: 2026-05-11-training-frontend
finding_id: "security-04"
nature: security
severity: P2
confidence: medium
suggested_action: cs-issue
status: fixed
---

# Finding 04：前端展示本地模拟邮箱验证码缺少环境闸门

## 速答

注册、找回密码、个人中心重置密码都会在后端返回 `mock_service === "local_email"` 时读取并展示验证码，但前端没有 `import.meta.env.DEV` 之类的环境闸门。

## 关键证据

- `frontend/src/config/api.ts:48` — `getLatestMockEmail()` 是通用导出函数，可直接请求 `/dev/mock-emails/latest`。
- `frontend/src/features/auth/components/RegisterForm.tsx:83` — 注册发送验证码后，只要响应为 `local_email` 就读取模拟邮箱。
- `frontend/src/features/auth/components/RegisterEmailCodeSection.tsx:64` — 注册表单会把 `debugCode` 直接展示在页面上。
- `frontend/src/features/auth/components/ResetPasswordModal.tsx:85` — 找回密码弹窗同样直接展示 `debugCode`。
- `frontend/src/features/profile/components/ProfileForm.tsx:266` — 个人中心密码重置也会读取模拟邮箱验证码。
- `frontend/src/features/profile/components/ProfileForm.tsx:271` — 若拿到验证码，还会通过 toast 展示本地模拟邮箱验证码。

## 影响

当前风险取决于部署环境是否启用本地模拟邮箱服务；如果线上误启用或 dev-tools 路由暴露，前端会主动展示注册/重置密码验证码。即使这是开发便利功能，也应该在前端和后端都加环境边界，避免配置失误变成验证码泄露。

## 修复方向

前端只在 `import.meta.env.DEV` 或显式 `VITE_ENABLE_LOCAL_MOCK_EMAIL_UI=true` 时调用和展示 mock email；生产构建下即使后端返回 `local_email` 也不展示验证码。

## 建议动作

`cs-issue`，因为涉及验证码泄露边界，应做安全加固并补生产模式下不展示 debug code 的测试。
