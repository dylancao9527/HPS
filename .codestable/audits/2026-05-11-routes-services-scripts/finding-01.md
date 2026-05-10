---
doc_type: audit-finding
audit: 2026-05-11-routes-services-scripts
finding_id: "security-01"
nature: security
severity: P1
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 01：本地模拟邮箱验证码查询接口启用后无鉴权暴露验证码

## 速答

`/api/dev/mock-emails/latest` 只要被注册就允许任意调用者按邮箱查询最近验证码，后端没有鉴权、环境二次确认或只允许本机访问的限制。

## 关键证据

- `backend/routes/dev_tools.py:9` — 直接声明 `GET /mock-emails/latest`，没有 `@token_required`、`@admin_required` 或其他守卫。
- `backend/routes/dev_tools.py:11` — 查询参数 `email` 由调用者任意提供，接口按该邮箱查找消息。
- `backend/routes/dev_tools.py:14` — 直接返回 `{"message": message}`，而消息对象包含验证码字段。
- `backend/services/mock_email_service.py:37` — 本地模拟邮件消息持久化 `recipient`、`scene`、`body` 和 `code`。
- `backend/services/mock_email_service.py:51` — `get_latest_email()` 只按 recipient/scene 过滤，不校验调用者身份。

## 影响

如果本地模拟邮箱服务在共享测试环境、演示环境或误配置环境中启用，任何能访问后端 API 的人只要知道邮箱，就能读取注册、改邮箱或重置密码验证码。前端已经有展示闸门，但后端接口本身仍是敏感数据出口。

## 修复方向

后端也增加环境和身份边界：默认关闭该 blueprint；启用时至少要求开发环境、管理员鉴权或本机访问，并且不要返回完整 message 对象。

## 建议动作

`cs-issue`，因为这是验证码泄露边界，适合补后端路由级安全测试。

## 修复结果

已修复。`/api/dev/mock-emails/latest` 默认只在启用本地模拟邮箱服务时注册，接口访问增加本机请求或 `X-Dev-Tools-Token` 开发令牌边界；响应只返回 `email`、`scene`、`code`、`created_at`，不再暴露完整邮件主题和正文。`.env.example` 已将本地模拟邮箱服务默认关闭。
