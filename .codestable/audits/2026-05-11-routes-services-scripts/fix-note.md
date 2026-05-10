---
doc_type: audit-fix-note
audit: 2026-05-11-routes-services-scripts
created: 2026-05-11
status: fixed
---

# routes-services-scripts 审计修复记录

## 修复范围

本次修复覆盖 `.codestable/audits/2026-05-11-routes-services-scripts/` 下 6 条 finding，代码范围限定在 `backend/routes/`、`backend/services/`、`backend/scripts/` 及对应测试。

## 代码变更

- `backend/routes/dev_tools.py`：本地模拟邮箱查询接口增加本机访问或 `X-Dev-Tools-Token` 开发令牌校验，响应只保留必要字段。
- `backend/config.py`、`backend/.env.example`：本地模拟邮箱服务默认关闭，并增加 `LOCAL_MOCK_EMAIL_ACCESS_TOKEN` 配置入口。
- `backend/services/auth_service.py`：验证码生成改用 `secrets`，缓存失败次数并在超过阈值后删除验证码；`AuthAccountService` 拆为注册、登录、账号维护、密码重置四个子服务，原门面接口保持不变。
- `backend/scripts/seed_demo_users.py`：默认预览不写库；写入需 `--apply`；删除旧 demo 用户需 `--reset-existing --yes-i-understand`；移除固定密码，改为显式参数、环境变量或运行时生成。
- `backend/services/bp_record_service.py`：非法 `recorded_at` 返回 400；列表分页复用统一限幅策略。
- `backend/services/admin_service.py`、`backend/routes/profile.py`：管理员用户列表和预测趋势查询复用统一分页/limit 限幅策略。

## 测试补充

- `backend/tests/routes/test_dev_tools_routes.py`：覆盖非本机访问拒绝、返回消息脱敏。
- `backend/tests/routes/test_auth_routes.py`：覆盖验证码错误次数达到阈值后失效。
- `backend/tests/scripts/test_seed_demo_users_cli.py`：覆盖默认预览、显式 `--apply`、删除确认参数。
- `backend/tests/routes/test_bp_records_routes.py`：覆盖分页限幅和非法 `recorded_at`。
- `backend/tests/routes/test_admin_routes.py`、`backend/tests/routes/test_profile_routes.py`：覆盖列表/趋势参数限幅。
- `backend/tests/services/test_service_architecture.py`：覆盖认证账户服务拆分边界。

## 验证

- 红灯确认：`uv run pytest tests\routes\test_dev_tools_routes.py tests\routes\test_auth_routes.py tests\routes\test_bp_records_routes.py tests\routes\test_admin_routes.py tests\routes\test_profile_routes.py tests\services\test_service_architecture.py tests\scripts\test_seed_demo_users_cli.py -q`，修复前 10 个目标失败。
- 目标回归：`uv run pytest tests\routes\test_dev_tools_routes.py tests\routes\test_auth_routes.py tests\routes\test_bp_records_routes.py tests\routes\test_admin_routes.py tests\routes\test_profile_routes.py tests\services\test_service_architecture.py tests\scripts\test_seed_demo_users_cli.py -q`，56 passed。
- 全量后端：`uv run pytest -q`，221 passed。
