# HPS 最后一轮架构清理计划

## 目标

对现有流程、数据读取和 Interface 做最后一轮收束：删除不再需要的旧 Interface，薄化必须保留的兼容入口，减少旧命名和旧缓存语义对后续维护的干扰。默认不修改数据库结构、迁移脚本或生产配置；若某阶段确实需要 schema 或部署配置变更，必须另行确认。

## 当前基线

状态：planned

- 工作区 `git status --short` 为空，当前可从干净状态开始。
- ADR-0007 已取代 ADR-0002，预测历史主结构是紧凑 `prediction_records`，不是多表 normalized storage。
- 领域文档已明确：普通用户入口固定为 **7天风险预测**；预测记录不可变；系统不是临床诊断系统。
- 之前阶段 24-29 已完成：每日血压序列读侧优化、今日健康任务收敛、周健康报告主命名、治理查询下推、compact mapper 主命名、Prophet lifecycle 旧 Interface 收束。

## 本轮可直接清理的旧 Interface 候选

| 候选 | 当前证据 | 建议 |
| --- | --- | --- |
| `PredictionRouteCacheService` | 生产代码无调用，只是旧测试/旧导入 shell | 删除 Module，并把测试迁到 `PredictionRunMetadataService` 或新 run metadata Module |
| `prediction.domain.cache_policy.build_cache_snapshot` | 只 re-export `build_prediction_run_snapshot`，生产无调用 | 删除旧 cache policy Export |
| 预测结果中的 `from_cache`、`cached_at`、`cache_expires_at`、`result_cache_hours`、`reuse_window_minutes` | 当前系统不 replay 旧预测结果，前端也未使用这些字段 | 从用户端结果 Interface 移除；保留内部 `cache_mode` 列作为 Prophet 模型复用/重训运行模式 |
| 新预测输入快照写入 `_cache_snapshot`、`_prophet_cache_key` | 新记录仍写入旧 key，污染 compact payload | 新写入只保留 `_model_state_snapshot`、`_prediction_run_key`；读取端继续兼容旧记录 |
| `/api/prophet-predictions` 与 `deleteProphetPrediction()` | 前端只用 GET 给个人中心风险趋势图，DELETE 未使用；后端实际读的是 `prediction_records` | 改为“预测趋势投影” Interface，删除旧 Prophet 命名和未使用 DELETE |
| `normalized_prediction_*` alias 与 `build_normalized_prediction()` fallback | 生产默认已使用 `CompactPredictionMapper`，normalized 只剩 alias 和兼容测试 | 删除 fallback；是否删除全部 alias 文件在阶段 3 最后确认 |
| `/api/auth/login` | 前端只使用 `/api/auth/login/user` 与 `/api/auth/login/admin` | 删除模糊登录入口，只保留角色明确的登录 Interface |
| `/api/dev/mock-emails/latest` | 本地验证码调试入口，但 blueprint 无条件注册 | 只在本地 mock email 开启时注册或返回 404，避免生产暴露开发 Interface |
| `WeeklyComparison*` 与 `/api/profile/weekly-comparison` | 之前确认保留兼容入口；现在若追求最终整洁可删除 | 阶段 5 单独确认；默认建议迁到 `/api/weekly-report` 并删除旧前端 alias |

## 阶段 0：保护网与接口清单

状态：complete

### 任务

- 运行后端和前端现有验证，记录本轮基线。
- 生成当前后端 route 清单和前端请求清单。
- 将所有待删 Interface 分为：生产仍用、仅前端旧调用、仅测试旧调用、完全无调用。

### 涉及文件

- `backend/routes/*.py`
- `frontend/src/features/**/api/*.ts`
- `backend/tests/**`
- `frontend/src/**/*.test.ts*`

### 验收

- `backend` 全量测试基线记录到 `progress.md`。
- `frontend` typecheck、lint、test 基线记录到 `progress.md`。
- 每个待删 Interface 都有调用证据，不能凭命名直接删除。

## 阶段 1：预测运行元信息与旧 cache 语义清理

状态：complete

### 任务

- 删除 `PredictionRouteCacheService` 和 `prediction.domain.cache_policy`。
- 从 `prediction.domain.__init__`、`prediction.domain.policies` 中移除 `build_cache_snapshot`。
- 将 `PredictionRunMetadataService` 收窄为只负责结果保留/元信息窗口，或直接把剩余能力并入更贴近预测运行的 Module。
- 从 `PredictionResult` 和序列化输出中移除旧结果缓存字段：`from_cache`、`cached_at`、`cache_expires_at`、`result_cache_hours`、`reuse_window_minutes`。
- 前端 `PredictionCacheMode` 删除 `hot_reuse`、`persistent_reuse` 等旧 result cache 模式，只保留当前真实模式。

### 涉及文件

- `backend/services/prediction_route_cache_service.py`
- `backend/services/prediction_run_metadata_service.py`
- `backend/prediction/domain/cache_policy.py`
- `backend/prediction/domain/__init__.py`
- `backend/prediction/domain/policies.py`
- `backend/prediction/schemas/results.py`
- `backend/prediction/application/prediction_result_builder.py`
- `backend/prediction/api/serializers.py`
- `frontend/src/types/prediction.ts`
- `backend/tests/routes/test_predictions_cache_helpers.py`
- `backend/tests/prediction/test_predict_use_case.py`
- `backend/tests/prediction/test_prediction_run_policies.py`

### 验收

- 新预测结果不再暴露旧 result cache 字段。
- Prophet 模型复用仍通过 `cache_mode="model_reuse"` 或后续更名的运行模式被治理统计识别。
- 后端目标测试和全量测试通过。

### 当前进展

- 已删除 `PredictionRouteCacheService` 和 `prediction.domain.cache_policy`。
- 已从 `prediction.domain.__init__`、`prediction.domain.policies` 移除 `build_cache_snapshot`。
- 已新增测试保护旧 cache Interface 不再可导入。
- 已删除 `PredictionRunMetadataService` 旧 cache-window/run-key Interface，保留 `PredictionRecordRetentionService`。
- 已从 `PredictionResult`、预测结果 builder 和历史 payload assembler 中移除旧 result cache 字段。
- 已从前端 `PredictionCacheMode` 移除 `hot_reuse`、`persistent_reuse`。
- `cache_mode` 继续保留，用于表达 `fresh_train` / `model_reuse` 运行模式和治理统计。

## 阶段 2：个人中心预测趋势投影 Interface 优化

状态：complete

### 任务

- 新增“预测趋势投影” Module，只为个人中心风险概率趋势图读取 `id`、`created_at`、`risk_probability`、`risk_level`。
- 替换 `/api/prophet-predictions` 为更准确的路径，例如 `/api/profile/prediction-trend` 或 `/api/predictions/trend`。
- 删除未使用的 `deleteProphetPrediction()` 前端函数和 `/api/prophet-predictions/<id>` 后端 route。
- 后端 repository 不再为趋势图组装完整预测 payload，不再携带 `bp_forecast`、`cache_key` 等旧字段。
- 前端 `ProfilePredictionListResponse` 命名改为 `ProfilePredictionTrendResponse`。

### 涉及文件

- `backend/routes/predictions.py`
- `backend/routes/profile.py`（如选择 profile 路径）
- `backend/prediction/application/list_prophet_predictions.py`
- `backend/prediction/application/delete_prophet_prediction.py`
- `backend/prediction/application/user_prediction_records.py`
- `backend/prediction/infrastructure/prediction_record_repository.py`
- `backend/prediction/infrastructure/repositories.py`
- `frontend/src/features/profile/api/profilePredictionApi.ts`
- `frontend/src/features/profile/components/PredictionTrendChart.tsx`
- `frontend/src/types/profile.ts`
- `backend/tests/routes/test_predictions_route_use_cases.py`

### 验收

- 个人中心风险趋势图行为不变。
- 后端趋势列表读取变成轻量投影，不依赖 `PredictionPayloadAssembler`。
- 旧 Prophet 命名不再出现在用户侧趋势 Interface。
- 如触及前端页面，浏览器验证 `/profile?tab=trend`。

### 当前进展

- 已将趋势读取入口迁到 `GET /api/profile/prediction-trend`，并在 `backend/routes/profile.py` 增加 `get_prediction_trend()`。
- 已删除旧用户侧 Prophet 趋势 Interface：
  - `backend/prediction/application/list_prophet_predictions.py`
  - `backend/prediction/application/delete_prophet_prediction.py`
  - `GET /api/prophet-predictions`
  - `DELETE /api/prophet-predictions/<id>`
- 已新增 `ListPredictionTrendUseCase`，并让 `PredictionUseCaseFactory`、`UserPredictionRecordActions`、`PredictionRepository.records` 统一走 `list_prediction_trend()`。
- `PredictionRecordRepository.list_prediction_trend()` 已改为只查询：
  - `id`
  - `created_at`
  - `risk_probability`
  - `risk_level`
- 前端个人中心趋势图已切到 `getPredictionTrend()`，`ProfilePredictionTrendResponse` / `RawProfilePredictionTrendRecord` 已取代旧 Prophet 命名。
- 已新增/更新红绿测试，覆盖：
  - profile 趋势 route 返回轻量 projection
  - predictions route 不再暴露旧 Prophet 趋势 helper
  - repository 边界不再调用 `PredictionPayloadAssembler`
  - 前端 API 请求路径改为 `/profile/prediction-trend`

## 阶段 3：compact mapper 后旧 normalized 兼容层收尾

状态：complete

### 任务

- `PredictionRecordRepository.save_prediction()` 只调用 `build_compact_prediction()`，删除 `build_normalized_prediction()` fallback。
- `PredictionInputSnapshot.to_persistence_payload()` 新写入不再包含 `_cache_snapshot` 和 `_prophet_cache_key`。
- `compact_prediction_input_mapping` 读取端保留旧 key fallback，以便旧记录可回放。
- 删除或收窄 `normalized_prediction_*` alias 文件与对应测试。推荐策略：保留顶层 `normalized_prediction_mapper.py` 一个过渡 alias，删除子模块 alias；若确认无外部导入，则全部删除。
- 删除 `backfill_normalized_storage.py` no-op 入口，或把它归档为文档说明而不是可调用代码。

### 涉及文件

- `backend/prediction/infrastructure/compact_prediction_mapper.py`
- `backend/prediction/infrastructure/compact_prediction_input_mapping.py`
- `backend/prediction/infrastructure/prediction_record_repository.py`
- `backend/prediction/infrastructure/normalized_prediction_*.py`
- `backend/prediction/infrastructure/backfill_normalized_storage.py`
- `backend/tests/prediction/test_compact_prediction_mapper.py`
- `backend/tests/prediction/test_normalized_prediction_mapper.py`
- `backend/tests/prediction/test_prediction_repository_boundaries.py`

### 验收

- 新预测记录 payload 不再包含旧 cache key。
- 旧记录读取兼容测试仍覆盖 `_prophet_cache_key` fallback。
- compact mapper 是唯一生产写入 Interface。
- 是否删除全部 normalized alias 有明确记录。

### 当前进展

- 已删除 `PredictionRecordRepository.save_prediction()` 对 `build_normalized_prediction()` 的 fallback，写入边界只剩 `build_compact_prediction()`。
- 已从 `PredictionInputSnapshot.to_persistence_payload()` 删除新写入对以下旧 key 的继续落库：
  - `_cache_snapshot`
  - `_prophet_cache_key`
- 已收紧 `compact_prediction_input_mapping.build_input_snapshot()`，新快照只保留实际传入的 metadata key，不再为旧 key 写入 `None` 占位。
- 已收紧 `assemble_input_data()`：
  - 新记录不再平铺 legacy key
  - 旧记录若仍带 `_cache_snapshot` / `_prophet_cache_key`，会映射回 `_model_state_snapshot` / `_prediction_run_key` 继续兼容读取
- 已从 `CompactPredictionWriteMapper` 删除 `build_normalized_prediction()` 旧写入 alias。
- 用户已确认执行激进删除方案。
- 已删除：
  - `backend/prediction/infrastructure/normalized_prediction_forecast_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_fusion_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_input_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_mapper.py`
  - `backend/prediction/infrastructure/normalized_prediction_recommendation_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_rows.py`
  - `backend/prediction/infrastructure/normalized_prediction_training_mapping.py`
  - `backend/prediction/infrastructure/backfill_normalized_storage.py`
- 已将相关测试改为断言这些旧模块不可再导入，并把架构文档主命名从 `normalized_prediction_mapper` 改为 `compact_prediction_mapper`。

## 阶段 4：认证与开发调试入口清理

状态：complete

### 任务

- 删除 `/api/auth/login`，只保留 `/api/auth/login/user` 与 `/api/auth/login/admin`。
- 调整认证测试，让普通用户和管理员登录都走角色明确的 Interface。
- `dev_tools_bp` 仅在 `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=True` 时注册，或 route 内在关闭时返回 404。
- 前端 `getLatestMockEmail()` 只在后端返回 `mock_service="local_email"` 后调用，保持现有行为；同时让开发调试失败不阻断真实注册/找回密码流程。

### 涉及文件

- `backend/routes/auth.py`
- `backend/services/auth_service.py`
- `backend/routes/dev_tools.py`
- `backend/app.py`
- `frontend/src/config/api.ts`
- `frontend/src/features/auth/components/RegisterForm.tsx`
- `frontend/src/features/auth/components/LoginForm.tsx`
- `frontend/src/features/profile/components/ProfileForm.tsx`
- `backend/tests/routes/test_auth_routes.py`

### 验收

- 用户登录和管理员登录语义明确。
- 生产配置关闭本地 mock email 时，开发调试入口不可用。
- 认证相关后端测试通过，前端 auth/profile 相关测试通过。

### 当前进展

- 已删除模糊登录 route：`POST /api/auth/login`。
- 保留并继续使用：
  - `POST /api/auth/login/user`
  - `POST /api/auth/login/admin`
- 前端无需改动登录调用链；`useAuth()` 原本就只根据角色选择 `/login/user` 与 `/login/admin`。
- `app.py` 已改为仅在 `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=True` 时注册 `dev_tools_bp`。
- 本地 mock email 关闭时，`/api/dev/mock-emails/latest` 不再注册；开启时保持原行为。
- 前端 `getLatestMockEmail()` 调用链维持现状：
  - 只在后端响应 `mock_service="local_email"` 后才请求调试接口
  - 关闭本地 mock email 时不会额外触发该接口
- 已同步更新：
  - `backend/tests/routes/test_auth_routes.py`
  - `backend/tests/routes/test_dev_tools_routes.py`
  - `README.md`

## 阶段 5：周健康报告兼容入口最终决策

状态：complete

### 最终决策

- 用户确认继续清理，已推翻上一轮“保留 `/api/profile/weekly-comparison` 兼容入口”的决定。
- 前后端统一只保留 `/api/weekly-report` 作为周健康报告主路径。

### 涉及文件

- `backend/routes/profile.py`
- `backend/services/weekly_comparison_service.py`
- `backend/tests/routes/test_profile_routes.py`
- `backend/tests/services/test_weekly_comparison_service.py`
- `frontend/src/features/profile/api/profileComparisonApi.ts`
- `frontend/src/features/profile/components/WeeklyComparisonPanel.tsx`
- `frontend/src/types/profile.ts`
- `frontend/src/pages/ProfilePage.tsx`

### 验收

- **周健康报告** 是唯一主语言。
- `/weekly-report` 和 `/profile?tab=trend` 均可渲染同一份周健康报告。
- 若删除旧 route，测试必须明确旧 route 已不存在或不再注册。

### 当前进展

- `ProfilePage` 已直接调用 `getWeeklyReport()`，不再使用 `getProfileWeeklyReport()`。
- 已删除前端兼容 alias：
  - `frontend/src/features/profile/api/profileComparisonApi.ts`
  - `frontend/src/features/profile/components/WeeklyComparisonPanel.tsx`
  - `frontend/src/features/profile/index.ts` 中的 `WeeklyComparisonPanel` / `getWeeklyComparison` 导出
  - `frontend/src/types/profile.ts` 中的 `WeeklyComparisonSummary`
- 已删除后端兼容入口：
  - `backend/routes/profile.py` 中的 `build_weekly_comparison_service()`
  - `backend/routes/profile.py` 中的 `GET /api/profile/weekly-comparison`
  - `backend/services/weekly_comparison_service.py`
- 已将周健康报告服务测试统一切回 canonical 文件：
  - 删除 `backend/tests/services/test_weekly_comparison_service.py`
  - 新增 `backend/tests/services/test_weekly_report_service.py`
- 已新增保护测试：
  - 旧 profile weekly-comparison route 不再暴露
  - `services.weekly_comparison_service` 不可再导入
  - 前端 weekly report API 走 `/weekly-report`

## 阶段 6：文档与计划收敛

状态：complete

### 已确认

- 当前有效文档需要清理旧 Interface 表述，避免误导后续开发。
- 历史记录文件保留旧 Interface 引用作为过程证据，不做伪历史清理。
- 历史记录文件包括 `findings.md`、`progress.md` 和 `docs/agents/final-interface-cleanup-phase0.md`。
- 如需降低 grep 噪声，只在历史记录文件顶部补充“历史扫描快照不代表当前 Interface”的说明。

### 任务

- 更新 `docs/architecture/ARCHITECTURE.md` 中仍提到 `normalized_prediction_mapper`、result cache 或旧 Prophet prediction history 的内容。
- 更新 `README.md`、`CONTEXT.md` 等当前有效说明中仍可能误导的旧 Interface 表述。
- 更新 `findings.md`，记录本轮删除/保留决策。
- 更新 `progress.md`，记录每阶段验证结果。
- 如某个旧 Interface 被保留，必须写明保留原因和未来删除条件。
- 删除 `backend/config.py` 中未使用的 `PROPHET_RESULT_CACHE_HOURS`，并同步移除 `README.md` 的环境变量示例。

### 涉及文件

- `docs/architecture/ARCHITECTURE.md`
- `CONTEXT.md`（仅当出现新领域术语时）
- `findings.md`
- `progress.md`
- `task_plan.md`

### 验收

- 架构文档与代码主命名一致：compact prediction record、周健康报告、7天风险预测、预测趋势投影。
- 历史扫描文件中的旧 Interface 引用被明确标记为历史证据，不当作当前架构说明处理。
- 不新增无必要 ADR；只有当保留旧 Interface 成为长期策略时再考虑 ADR。
- 未使用的 result-cache 配置项已从生产配置和示例环境变量中删除。

### 当前进展

- 已更新 `CONTEXT.md`，将 `weekly-comparison` 标记为历史兼容叫法，不再是当前接口或领域语言。
- 已从 `backend/config.py` 删除 `PROPHET_RESULT_CACHE_HOURS`。
- 已从 `README.md` 的环境变量示例删除 `PROPHET_RESULT_CACHE_HOURS`。
- 已在 `findings.md`、`progress.md` 和 `docs/agents/final-interface-cleanup-phase0.md` 顶部补充“历史扫描快照不代表当前 Interface”的说明。
- 后端全量测试通过：`uv run pytest`，189 passed。
- 前端验证通过：`pnpm run typecheck`、`pnpm run lint`、`pnpm run test`。

## 推荐执行顺序

1. 阶段 0：保护网与接口清单。
2. 阶段 1：预测运行元信息与旧 cache 语义清理。
3. 阶段 2：个人中心预测趋势投影 Interface 优化。
4. 阶段 3：compact mapper 后旧 normalized 兼容层收尾。
5. 阶段 4：认证与开发调试入口清理。
6. 阶段 5：周健康报告兼容入口最终决策。
7. 阶段 6：文档与计划收敛。
8. 阶段 7：论文准备最终体检与演示包收口。
9. 阶段 8：论文正式写作与交付计划。

## 验证矩阵

- 后端目标测试：
  - `uv run pytest tests/routes/test_predictions_route_use_cases.py tests/routes/test_predictions_cache_helpers.py`
  - `uv run pytest tests/prediction/test_compact_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py`
  - `uv run pytest tests/routes/test_auth_routes.py tests/routes/test_profile_routes.py tests/routes/test_weekly_report_routes.py`
- 后端全量：
  - `uv run pytest`
- 前端目标测试：
  - `pnpm exec vitest run src/pages/ProfilePage.test.tsx src/features/prediction/api/predictApi.test.ts src/features/auth/validation.test.ts`
- 前端全量：
  - `pnpm run typecheck`
  - `pnpm run lint`
  - `pnpm run test`
- 浏览器验证：
  - `/profile?tab=trend`
  - `/weekly-report`
  - `/predict`
  - `/login`
  - `/admin/login`

## 风险控制

- 不修改数据库结构、迁移脚本或生产配置。
- 删除 route 前先确认前端已经不调用。
- 删除 alias 前先用 `rg` 确认生产代码无导入。
- 每个阶段单独验证，失败时回到当前阶段，不连带改下一阶段。
- 阶段 0-6 不触碰 `backend/static/` 构建产物；阶段 7 发现本地静态产物已落后当前源码后，仅刷新被 `.gitignore` 忽略的演示构建产物，不把它作为源码 Interface 变更。

## 阶段 7：论文准备最终体检与演示包收口

状态：complete

### 目标

面向论文答辩和单服务演示，再做一轮缺陷扫描：确认旧 Interface 不会从当前源码或静态构建产物中漏出，清理本地生成缓存，并识别是否值得增加一个论文准备期的新功能。

### 已发现

- `backend/static` 是被 `.gitignore` 忽略的构建产物，但当前本地旧构建仍引用已删除的 `/api/prophet-predictions` 和 `/api/profile/weekly-comparison`；如果使用 `start.bat --skip-build`，可能服务到旧前端。
- 当前生产源码旧 Interface 关键词基本只剩保护测试和历史说明；这类命中不是当前缺陷。
- 后端迁移脚本中仍有 `prophet_predictions` 和旧预测明细表引用，属于历史迁移链和 compact-storage 迁移回填逻辑；不应在论文准备期直接删除或改写迁移历史。
- 前端预测趋势图错误提示仍写“预测历史接口状态”，命名不够贴合当前“预测趋势投影” Interface，已改为“预测趋势接口状态”。

### 任务

- 刷新 `backend/static`，确保单服务演示静态产物不再引用旧 Interface。
- 清理项目源码范围内的 `__pycache__` 与临时测试缓存，不动 `.venv`、`backend/runtime`、`backend/ml_models`。
- 更新 `findings.md` 和 `progress.md`，记录本轮缺陷和新功能建议。
- 重新运行后端、前端验证与静态构建扫描。

### 新功能候选

- 推荐候选：新增“演示准备检查”命令或脚本，自动检查后端测试、前端测试、静态构建是否过期、旧 Interface 关键词是否进入有效产物，并输出论文答辩前检查结果。
- 备选候选：新增“论文材料导出”命令，从当前路由、模型报告和架构文档生成论文附录草稿。
- 暂不建议：答辩前新增业务交互功能；这会增加测试和演示风险。

### 当前进展

- 已刷新 `backend/static` 本地演示构建产物，旧 Interface 关键词不再出现在静态构建中。
- 已清理项目源码范围内的 `__pycache__`、`.pytest_cache` 和 `tsconfig.node.tsbuildinfo`，不触碰 `.venv`、`backend/runtime`、`backend/ml_models`。
- 已将前端预测趋势图错误提示从“预测历史接口状态”改为“预测趋势接口状态”。
- 静态扫描确认旧 Interface 关键词只剩保护测试中的不可存在断言。
- 后端全量测试通过：`uv run pytest`，189 passed。
- 前端验证通过：`pnpm run typecheck`、`pnpm run lint`、`pnpm run test`，18 files / 36 tests passed。
- 前端生产构建通过：`pnpm build`。

## 阶段 8：论文正式写作与交付计划

状态：in_progress

### 目标

基于已确认的论文题目《基于Prophet与LightGBM的高血压风险预测系统设计与实现》、模型类样文、学校撰写规范、任务书/开题报告和当前项目实现，完成一篇以 Prophet 与 LightGBM 双模型预测链路为主线的本科毕业论文，并交付主论文、图表源码附件、参考文献核验清单和截图资源清单。

### 资料目录

- 论文输入资料与生成资料统一集中在 `lunwen-doc/`。
- 学校规范、样文、任务书、开题报告等原始资料保留在 `lunwen-doc/` 根目录。
- 参考文献池、图片清单、图表截图和后续成稿统一放在 `lunwen-doc/论文写作材料/`。
- 样式分析、文本抽取、临时截图、临时日志和脚本验证结果等中间产物统一放在 `output/lunwen-intermediate/`。

### 总体写作原则

- 论文主线围绕 Prophet 血压趋势预测、LightGBM 风险分类、双模型预测链路、模型训练结果和系统落地展开。
- 数据库、权限、用户管理、后台管理只作为预测链路支撑内容，不写成传统 CRUD 管理系统。
- 正文尽量不放真实源码；优先使用公式、流程图、模型设计图、E-R 图、接口表、数据结构表、页面截图和文字说明。
- 第4章必须先解释模型链路，再展示系统落地；模型设计图与系统页面截图分开命名。
- 不把盐摄入量、睡眠时长写成当前已实现模型输入，只可在展望中作为后续扩展风险因素。
- 统一使用《中国高血压防治指南（2024年修订版）》口径；系统定位为风险预测辅助系统，不写成临床诊断系统。

### 已冻结目录

```text
第1章  绪论
§1.1 研究背景及意义
§1.2 国内外研究现状
§1.3 研究方法与内容

第2章  相关理论介绍
§2.1 时间序列预测
§2.2 Prophet模型
§2.3 LightGBM模型
§2.4 本章小结

第3章  实验数据集与评价指标
§3.1 实验数据集介绍
§3.2 数据预处理与特征构建
§3.3 模型评价指标
§3.4 本章小结

第4章  双模型预测原理与系统设计
§4.1 Prophet血压趋势预测方法
§4.2 LightGBM风险分类方法
§4.3 双模型预测链路设计
§4.4 系统数据结构设计
§4.5 系统界面设计
§4.6 本章小结

第5章  模型训练、实验结果与系统测试
§5.1 实验环境
§5.2 LightGBM训练结果分析
§5.3 特征重要性分析
§5.4 Prophet运行策略分析
§5.5 系统功能测试
§5.6 本章小结

第6章  总结与展望
§6.1 总结
§6.2 展望
```

### 字数预算

| 部分 | 目标字数/字符 | 说明 |
| --- | ---: | --- |
| 中文摘要 | 500-700 | 背景、方法、系统、结果 |
| 英文摘要 | 350-500 words | 与中文摘要对应 |
| 第1章 | 2200-2600 | 绪论与研究现状 |
| 第2章 | 2500-3000 | Prophet、LightGBM 和理论基础 |
| 第3章 | 2200-2600 | 数据集、预处理、特征构建和评价指标公式 |
| 第4章 | 4300-5000 | 全文最长章，模型设计图、数据结构和界面截图 |
| 第5章 | 3000-3600 | 模型训练结果、特征重要性、Prophet 策略和系统测试 |
| 第6章 | 700-1000 | 总结与展望 |
| 正文合计 | 15000-17800 | 贴近模型类样文，不刻意写厚 |

### 写作阶段拆分

#### 8.1 参考文献池检索与核验

状态：complete

任务：

- 建立约 15 篇真实可核验参考文献池，优先 2020 年以后文献。
- 按中文优先原则控制中英文比例，目标约为中文:英文 = 8:2。
- 覆盖高血压指南与防治、高血压风险预测、Prophet/时间序列预测、LightGBM/树模型分类、健康管理系统。
- 记录 DOI、期刊/会议、年份、作者、可访问链接和引用用途。
- 任务书中的 3 本工具书只作为低优先级补充，不作为主要参考文献来源。

产物：

- `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献核验清单.json`
- `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献池.md`

当前进展：

- 已按用户要求调整为中文优先参考文献池：共 15 篇，其中中文 12 篇、英文 3 篇，比例为 80%:20%。
- 中文文献覆盖高血压指南与防治、健康管理规范、流行病学背景、中文高血压风险预测、中文机器学习健康风险预测、可解释机器学习和 Prophet 中文应用。
- 英文文献仅保留 Prophet 原始论文、LightGBM 原始论文和 1 篇高相关高血压可视化风险预测系统论文。
- 已通过 Crossref、OpenAlex、PubMed、Unpaywall、期刊官网、DBLP、NeurIPS Proceedings 和中文期刊页面进行核验。
- 参考文献核验清单 JSON 已通过语法校验。
- Semantic Scholar batch API 本次触发 429，已改用 OpenAlex 引用量作为引用参考并记录在核验清单。
- 中国高血压防治指南（2024年修订版）未被 Crossref/OpenAlex 收录，但已通过《中华高血压杂志（中英文）》官网和公开 PDF 核验。
- LightGBM 原始论文未发现稳定 Crossref DOI，已通过 DBLP、NeurIPS 页面和 NeurIPS PDF 核验。

#### 8.2 图表与截图资产准备

状态：complete

任务：

- 绘制 Prophet 血压趋势预测流程图。
- 绘制 LightGBM 风险分类输入输出图。
- 绘制 Prophet-LightGBM 双模型预测链路图。
- 绘制预测结果治理链路图。
- 绘制核心数据结构 E-R 图。
- 启动系统并抓取第4章页面截图：风险因素档案页、血压记录页、风险预测页、预测结果页、预测历史页、预测结果治理页。

产物：

- `lunwen-doc/论文写作材料/thesis-assets/` 下的 `.mmd` / `.png` / 截图文件。
- `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-图片清单.md`
- 图表源码后续进入附件 `.docx`。

当前进展：

- 已创建 `lunwen-doc/论文写作材料/thesis-assets/diagrams/` 与 `lunwen-doc/论文写作材料/thesis-assets/screenshots/`。
- 已生成并导出 5 张第4章图表：
  - `figure-4-1-prophet-bp-trend-flow`
  - `figure-4-2-lightgbm-risk-io`
  - `figure-4-3-prophet-lightgbm-pipeline`
  - `figure-4-4-prediction-governance-flow`
  - `figure-4-5-core-er`
- 每张图已保留 `.mmd`、`.png` 和 `.svg` 版本。
- `mmdc` 初次因 Puppeteer 未找到 Chrome 失败；已显式指定本机 Chrome 路径后成功导出。
- 已通过演示用户 `demo_showcase_high` 运行真实 7 天预测，并抓取 6 张第4章页面截图：
  - `figure-4-6-risk-factor-profile-page.png`
  - `figure-4-7-bp-records-page.png`
  - `figure-4-8-risk-prediction-page.png`
  - `figure-4-9-prediction-result-page.png`
  - `figure-4-10-prediction-history-page.png`
  - `figure-4-11-prediction-governance-page.png`
- 已创建图片清单，记录图题、文件路径、章节放置位置和截图尺寸。
- Playwright 抓图后用户端与管理员端控制台均无 error。

#### 8.3 章节正文写作

状态：in_progress（Markdown 初稿已完成，待二轮润色和 Word 转换）

任务顺序：

1. 先写第3章，固定数据集、预处理、预测期血压特征和评价指标公式。
2. 再写第4章，固定 Prophet、LightGBM、双模型链路、数据结构和界面设计。
3. 写第5章，使用 `docs/model_report.md` 中的真实 LightGBM 指标、特征重要性和 Prophet 运行策略。
4. 回写第1章研究背景与现状，按已核验文献补引用。
5. 写第2章相关理论介绍，控制公式和算法解释篇幅。
6. 写第6章总结与展望，扩展项可包括盐摄入、睡眠时长、多源数据、模型校准和更多外部验证。
7. 写中英文摘要、关键词、致谢和参考文献。

约束：

- 每完成一章统计字数，超出预算时先压缩泛泛背景和重复系统描述。
- 不虚构临床实验、医院数据、深度学习训练流程或 Prophet 精度指标。
- LightGBM 指标只评价风险分类模型；Prophet 主要说明预测策略、训练窗口、置信度和系统运行方式。

当前进展：

- 已生成主论文 Markdown 初稿：`lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现.md`。
- 初稿已包含中英文摘要、关键词、第1章至第6章、致谢和参考文献。
- 初稿已插入第4章 11 张图表/截图的 Markdown 图片引用。
- 已完成图片路径校验、参考文献核验清单 JSON 校验和基础结构统计。

#### 8.4 Word 成稿与附件交付

状态：pending

任务：

- 按学校规范生成主论文 `.docx`。
- 生成附件 `.docx`，收录 Mermaid/PlantUML 图源码、E-R 图源码、关键流程图源码和必要说明。
- 检查标题层级、图题表题、摘要、关键词、参考文献顺序、分页和目录。
- 渲染抽查 `.docx` 页面，确认图片不糊、图题表题不漂移、章节顺序正确。

产物：

- `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现.docx`
- `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-附件.docx`
- `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-图片清单.md`

### 第4章图表清单

| 编号建议 | 类型 | 名称 | 放置位置 |
| --- | --- | --- | --- |
| 图4-1 | 模型设计图 | Prophet 血压趋势预测流程图 | §4.1 |
| 图4-2 | 模型设计图 | LightGBM 风险分类输入输出图 | §4.2 |
| 图4-3 | 模型设计图 | Prophet-LightGBM 双模型预测链路图 | §4.3 |
| 图4-4 | 流程设计图 | 预测结果治理链路图 | §4.3 或 §4.5 |
| 图4-5 | 数据结构图 | 核心数据结构 E-R 图 | §4.4 |
| 表4-1 | 数据表 | 核心数据结构说明表 | §4.4 |
| 图4-6 | 页面截图 | 风险因素档案页 | §4.5 |
| 图4-7 | 页面截图 | 血压记录页 | §4.5 |
| 图4-8 | 页面截图 | 风险预测页 | §4.5 |
| 图4-9 | 页面截图 | 预测结果页 | §4.5 |
| 图4-10 | 页面截图 | 预测历史页 | §4.5 |
| 图4-11 | 页面截图 | 预测结果治理页 | §4.5 |

### 公式与算法表达计划

| 位置 | 内容 | 表达方式 |
| --- | --- | --- |
| 第2章 | Prophet 加性模型 | `y(t)=g(t)+s(t)+h(t)+epsilon_t` |
| 第2章 | LightGBM/GBDT 加法模型 | 多棵回归树加法模型与概率输出说明 |
| 第3章 | 日均血压聚合 | 日均收缩压、日均舒张压公式 |
| 第3章 | 预测期血压特征 | 未来 7 天预测收缩压均值、舒张压均值 |
| 第3章 | 分类指标 | Accuracy、Precision、Recall、F1、AUC、PR-AUC、Brier Score |
| 第4章 | 风险融合策略 | 只作为工程策略说明，不夸大为临床风险模型 |
| 第4章 | 双模型预测流程 | 流程图 + 极短伪代码或核心逻辑摘要 |

### 验收标准

- 论文事实与 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md`、`docs/model_report.md` 一致。
- 第4章是全文最长章节，且模型设计图位于页面截图之前。
- 正文不大量粘贴真实源码，数据库设计不扩写成独立主线。
- 参考文献真实可核验，且正文引用顺序与参考文献列表一致。
- 主论文、附件、图片清单和参考文献核验清单均使用论文题目命名。
- 生成 `.docx` 后完成至少一次格式与图片渲染检查。

### 风险控制

- 若用户补充新的学校模板、样文、任务书或封面字段，先回到资料分析与样式确认，不直接沿旧计划开写。
- 若文献检索结果不足，不用猜测型引用；宁可减少数量，也要保证可核验。
- 若截图环境无法启动，先记录阻塞并生成图表/正文占位清单，不伪造系统截图。
- 若模型训练报告被重新生成，先更新第5章数据表和图表，不沿用旧指标。

