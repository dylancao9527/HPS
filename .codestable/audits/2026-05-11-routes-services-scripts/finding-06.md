---
doc_type: audit-finding
audit: 2026-05-11-routes-services-scripts
finding_id: "maintainability-06"
nature: maintainability
severity: P2
confidence: high
suggested_action: cs-refactor
status: fixed
---

# Finding 06：AuthAccountService 聚合验证码、登录和账号维护流程，修改风险偏高

## 速答

`auth_service.py` 把验证码签发、注册、登录、改密码、改邮箱、找回密码和重置密码都集中在同一服务文件/类里，后续安全加固容易互相牵连。

## 关键证据

- `backend/services/auth_service.py:14` — `EmailCodeService` 单类已经覆盖验证码生成、缓存、冷却、校验、本地模拟邮件投递和响应体构造。
- `backend/services/auth_service.py:119` — `AuthAccountService` 从这里开始，类长度约 253 行。
- `backend/services/auth_service.py:124` — 同一类处理发送注册验证码。
- `backend/services/auth_service.py:145` — 同一类处理注册。
- `backend/services/auth_service.py:192` — 同一类处理用户/管理员登录。
- `backend/services/auth_service.py:237` — 同一类处理登录态改密码。
- `backend/services/auth_service.py:259` — 同一类处理修改邮箱验证码。
- `backend/services/auth_service.py:323` — 同一类处理找回密码。
- `backend/services/auth_service.py:343` — 同一类处理邮箱验证码重置密码。

## 影响

Finding 1 和 Finding 2 的安全加固都要碰这个文件；如果继续在同一类里追加限流、失败锁定、审计日志和环境策略，类会更长，测试也更难聚焦。当前不是立即功能错误，但维护成本已经超过普通业务服务。

## 修复方向

按认证子域拆分：验证码服务、注册服务、登录服务、账号资料服务、密码重置服务；路由层仍保持当前 API，不改变外部契约。

## 建议动作

`cs-refactor`，因为这是行为不变的结构整理，应在修完验证码安全边界后再拆。

## 修复结果

已修复。`AuthAccountService` 保留为路由层门面，内部拆为 `RegistrationService`、`LoginService`、`AccountMaintenanceService`、`PasswordResetService`，验证码、登录、账号维护和密码重置的修改边界更清晰。
