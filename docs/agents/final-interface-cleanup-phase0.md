# 最后一轮旧 Interface 清理：阶段 0 保护网与接口清单

> 注：本文是 2026-05-08 阶段 0 的历史扫描快照，保留旧 Interface 命中作为删除前证据，不代表当前接口清单。

时间：2026-05-08 17:41 +08:00

## 验证基线

- 后端：`cd backend; uv run pytest` 通过，190 passed。
- 前端：`cd frontend; pnpm run typecheck` 通过。
- 前端：`cd frontend; pnpm run lint` 通过。
- 前端：`cd frontend; pnpm run test` 通过，16 files / 34 tests passed。

## 后端 route 清单

- `/api/admin/users`：GET。
- `/api/admin/users/<account_id>`：PUT、DELETE。
- `/api/admin/users/batch`：DELETE。
- `/api/admin/export/training`：GET。
- `/api/admin/stats`：GET。
- `/api/admin/governance/predictions`：GET。
- `/api/admin/governance/predictions/<prediction_id>`：GET。
- `/api/admin/governance/export`：GET。
- `/api/auth/send-register-code`：POST。
- `/api/auth/register`：POST。
- `/api/auth/login`：POST。
- `/api/auth/login/user`：POST。
- `/api/auth/login/admin`：POST。
- `/api/auth/me`：GET。
- `/api/auth/change-password`：POST。
- `/api/auth/send-change-email-code`：POST。
- `/api/auth/update-account`：POST。
- `/api/auth/forgot-password`：POST。
- `/api/auth/reset-password`：POST。
- `/api/bp-records`：GET、POST。
- `/api/bp-records/<record_id>`：DELETE。
- `/api/bp-records/batch`：DELETE。
- `/api/dev/mock-emails/latest`：GET。
- `/api/health-tasks/today`：GET。
- `/api/predict`：POST。
- `/api/predictions`：GET。
- `/api/predictions/<pred_id>`：DELETE。
- `/api/predictions/batch`：DELETE。
- `/api/prophet-predictions`：GET。
- `/api/prophet-predictions/<pred_id>`：DELETE。
- `/api/bp-data-status`：GET。
- `/api/profile`：GET、PUT。
- `/api/profile/weekly-comparison`：GET。
- `/api/weekly-report`：GET。

## 前端请求清单

- `config/api.ts`：所有普通请求走 `request()`，基础前缀为 `/api`。
- `config/api.ts`：`GET /api/dev/mock-emails/latest`，由本地 mock email 调试流程使用。
- `hooks/useAuth.tsx`：登录只调用 `/api/auth/login/user` 或 `/api/auth/login/admin`。
- `auth/RegisterForm.tsx`：`POST /api/auth/send-register-code`。
- `auth/LoginForm.tsx`：`POST /api/auth/forgot-password`、`POST /api/auth/reset-password`。
- `weekly-report/api/weeklyReportApi.ts`：`GET /api/weekly-report`、`GET /api/profile/weekly-comparison`。
- `prediction/api/predictApi.ts`：`POST /api/predict`、`GET /api/bp-data-status?forecast_days=7`。
- `admin/api/adminApi.ts`：管理员用户、统计、预测治理列表/详情/导出接口。
- `bp-records/api/bpApi.ts`：`GET/POST /api/bp-records`、`DELETE /api/bp-records/<id>`、`DELETE /api/bp-records/batch`。
- `health-tasks/api/healthTaskApi.ts`：`GET /api/health-tasks/today`。
- `history/api/historyApi.ts`：`GET /api/predictions`、`DELETE /api/predictions/<id>`、`DELETE /api/predictions/batch`。
- `profile/api/profileApi.ts`：`GET/PUT /api/profile`，以及账号、邮箱、密码相关 `/api/auth/*` 接口。
- `profile/api/profilePredictionApi.ts`：`GET /api/prophet-predictions?limit=...`；同文件导出 `deleteProphetPrediction()` 调用 `DELETE /api/prophet-predictions/<id>`。

## 待删 Interface 调用证据分类

| Interface | 分类 | 当前证据 |
| --- | --- | --- |
| `PredictionRouteCacheService` | 完全无外部调用 | 生产扫描只命中 `backend/services/prediction_route_cache_service.py` 自身。 |
| `prediction.domain.cache_policy.build_cache_snapshot` | 兼容 export，无生产调用方 | 生产扫描只命中 `cache_policy.py`、`prediction.domain.__init__` 和 `prediction.domain.policies` re-export。 |
| `PredictionResult.from_cache`、`cached_at`、`cache_expires_at`、`reuse_window_minutes`、`result_cache_hours` | 生产仍暴露，前端未使用，测试仍断言 | 后端 schema/result builder/serializer 仍输出；前端生产代码未消费这些字段；后端测试断言存在。 |
| `PredictionCacheMode.hot_reuse`、`persistent_reuse` | 前端类型残留 | 只在 `frontend/src/types/prediction.ts` 类型定义中出现。 |
| 新预测输入快照 `_cache_snapshot`、`_prophet_cache_key` | 生产仍写入旧 key，读取兼容仍需要 | `PredictionInputSnapshot.to_persistence_payload()` 仍写入；migration 与测试覆盖旧记录兼容。 |
| `/api/prophet-predictions` GET | 生产仍被个人中心趋势图调用 | `PredictionTrendChart` 通过 `getProphetPredictions(120)` 调用；后端读取 `prediction_records` 并返回风险趋势所需字段。 |
| `/api/prophet-predictions/<id>` DELETE 与 `deleteProphetPrediction()` | 前端 API 函数残留，未被组件调用 | 只在 `profilePredictionApi.ts` 导出；组件未导入；后端 route 与测试仍覆盖。 |
| `normalized_prediction_*` alias 与 `build_normalized_prediction()` fallback | 生产兼容 fallback + 测试兼容 | 生产侧 `PredictionRecordRepository.save_prediction()` 仍 fallback；测试仍验证旧 normalized 导入和 legacy alias。 |
| `/api/auth/login` | 仅后端 route 和测试旧调用 | 前端登录只走 `/api/auth/login/user` 与 `/api/auth/login/admin`；后端测试仍覆盖模糊登录入口。 |
| `/api/dev/mock-emails/latest` | 生产 route 暴露，本地调试流程按条件调用 | `app.py` 无条件注册 `dev_tools_bp`；前端只在响应 `mock_service="local_email"` 后调用。 |
| `/api/profile/weekly-comparison` 与 `WeeklyComparison*` | 生产仍用的兼容入口 | Profile 趋势 tab 通过 `getProfileWeeklyReport()` 调用 `/profile/weekly-comparison`；服务和前端 alias 仍保留。 |

## 阶段 0 工具错误

| 错误 | 尝试次数 | 解决方案 |
| --- | --- | --- |
| PowerShell 前端请求扫描命令存在多余 `}`，解析失败 | 2 | 改用更窄的 `rg` 扫描，并排除 `backend/static`、测试和规划文件噪声。 |
