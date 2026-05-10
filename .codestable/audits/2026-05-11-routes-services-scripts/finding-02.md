---
doc_type: audit-finding
audit: 2026-05-11-routes-services-scripts
finding_id: "security-02"
nature: security
severity: P1
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 02：邮箱验证码校验没有失败次数限制，重置密码可被在线撞码

## 速答

邮箱验证码有发送冷却，但校验阶段没有失败次数计数或锁定；`reset-password` 是公开接口，攻击者可在验证码有效期内对同一邮箱持续尝试 6 位码。

## 关键证据

- `backend/services/auth_service.py:21` — 验证码使用 `random.randint` 注入，默认不是面向安全验证码的 CSPRNG。
- `backend/services/auth_service.py:30` — `generate_code()` 固定生成 6 位数字码。
- `backend/services/auth_service.py:66` — `verify_code()` 只读取缓存并比较验证码。
- `backend/services/auth_service.py:73` — 验证失败只返回“验证码错误”，没有递增失败次数、锁定缓存或延长冷却。
- `backend/routes/auth.py:162` — `/reset-password` 是未登录公开接口。
- `backend/services/auth_service.py:359` — 重置密码只调用 `verify_code(email, code)`，没有额外尝试频率限制。

## 影响

单个验证码 TTL 默认 300 秒，攻击面主要在注册、修改邮箱和重置密码，其中重置密码影响最大。即使 6 位码空间不小，缺少失败次数限制会让安全性依赖外围限流；当前代码内没有看到 IP/账号维度的尝试计数。

## 修复方向

使用 `secrets` 生成验证码，并在 `code_store` 中记录失败次数；超过阈值后删除或锁定验证码，同时对重置密码接口增加账号/IP 维度限流。

## 建议动作

`cs-issue`，因为这是认证安全边界问题，需要补“多次错误验证码后拒绝”的回归测试。

## 修复结果

已修复。验证码生成改用 `secrets` 支撑的随机数；验证码缓存记录失败次数，连续错误达到阈值后删除验证码并要求重新获取，注册、修改邮箱和重置密码共用该校验边界。
