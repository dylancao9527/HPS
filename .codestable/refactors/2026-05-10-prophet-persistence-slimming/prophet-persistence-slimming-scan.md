---
doc_type: refactor-scan
refactor: 2026-05-10-prophet-persistence-slimming
status: user-reviewed
scope: Prophet model persistence metadata, asset storage keys, and fixed 7-day persistence call paths in backend model/infrastructure/tests.
summary: "Found 3 optimization items: structure 2 / readability 1 / performance 0."
---

# prophet-persistence-slimming scan

## 总览

- 扫描范围：`backend/models/user_prophet_model.py`, `backend/prediction/infrastructure/prophet_model_store.py`, `backend/prediction/infrastructure/prophet_model_repository.py`, `backend/prediction/infrastructure/prophet_gateway.py`, `backend/prediction/infrastructure/prophet_asset_maintenance.py`, `backend/prediction/infrastructure/prophet_trainer.py`, `backend/prediction/infrastructure/prophet_training_context.py`, `backend/prediction/domain/run_key_policy.py`, `backend/tests/prediction/test_prophet_gateway.py`, `backend/tests/prediction/test_forecast_period_policy.py`, `backend/tests/prediction/test_prediction_repository_boundaries.py`
- 发现 3 条优化点：结构 2 / 性能 0 / 可读性 1
- 按风险：低 0 / 中 3 / 高 0
- 建议先做：#1 #2（两者都直接来自 7 天固定周期，且已有测试能覆盖路径/仓储行为）
- 建议慎做 / 后做：#3（会修改 `user_prophet_models` 表字段，必须先确认数据库迁移范围）
- 前置检查 7 条全过：✓

## 条目

### #1 把 Prophet 资产路径里的 `fd_7` 槽位移除 ✓

- **位置**：`backend/prediction/infrastructure/prophet_model_store.py:28-29`, `backend/prediction/infrastructure/prophet_asset_maintenance.py:17-23`, `backend/prediction/infrastructure/prophet_gateway.py:142-147`
- **分类**：结构
- **现状**：`LocalProphetModelStore.build_storage_key()` 生成 `user_<user_id>/fd_<forecast_days>/<model_version>/<data_signature>`，但 `forecast_days` 已被策略固定为 7。
- **问题**：同一个固定值在资产路径、回填命令和持久化入口重复传递 3 次；`list_storage_keys()` 只扫描 `user_*/fd_*/*/*`，新旧路径共存时没有兼容枚举口径。
- **建议**：把新写入路径改为 `user_<user_id>/<model_version>/<data_signature>`，同时让清理枚举兼容旧 `fd_7` 路径和新路径，避免误删已引用资产。
- **建议映射的方法**：M-L1-01（Parallel Change 并行变更）
- **风险**：中（文件资产路径是持久化标识，需要兼容已有 `storage_key`）
- **验证**：AI 自证（新增/更新 store 单测；跑 `uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_forecast_period_policy.py`）
- **范围**：约 45 行 / 3 文件

### #2 移除 `user_prophet_models.forecast_days` 槽位字段 ✓

- **位置**：`backend/models/user_prophet_model.py:7-24`, `backend/prediction/infrastructure/prophet_model_repository.py:11-31`, `backend/prediction/infrastructure/prophet_model_repository.py:96-115`, `backend/migrations/versions/9c1d2e3f4a5b_profile_risk_factor_split_and_indexes.py:300-303`
- **分类**：结构
- **现状**：`user_prophet_models` 仍保存 `forecast_days`，并用 `(user_id, forecast_days, is_active, trained_at, id)` 建活跃模型索引；查询、失活和清理也按 `(user_id, forecast_days)` 分槽。
- **问题**：预测周期已统一为 7 天后，`forecast_days` 列和 check constraint 只能保存单一值；活跃模型槽位分组字段比实际业务维度多 1 个。
- **建议**：新增迁移删除 `forecast_days` 列和 7 天 check constraint，将活跃模型索引改为 `(user_id, is_active, trained_at, id)`，仓储接口内部按用户维度管理活跃 Prophet 模型；外层 `forecast_days` 参数暂保留给现有 API 校验链路。
- **建议映射的方法**：M-L1-01（Parallel Change 并行变更）
- **风险**：中（涉及数据库结构和迁移脚本；项目注意事项要求先确认）
- **验证**：AI 自证（迁移脚本静态检查；跑 `uv run pytest tests/prediction/test_forecast_period_policy.py tests/prediction/test_prediction_repository_boundaries.py tests/prediction/test_prophet_gateway.py`）
- **范围**：约 80 行 / 5 文件

### #3 删除固定 7 天下可推导的 Prophet 元数据列 ✗

用户选择：暂不做。

- **位置**：`backend/models/user_prophet_model.py:27-36`, `backend/prediction/infrastructure/prophet_gateway.py:127-166`, `backend/prediction/infrastructure/prophet_trainer.py:24-56`, `backend/prediction/infrastructure/prophet_training_context.py:144-156`
- **分类**：可读性
- **现状**：模型表保存 `aggregation_mode`, `weekly_enabled`, `monthly_enabled`；其中 `aggregation_mode` 是固定 `daily_mean`，`monthly_enabled` 在 7 天预测分支恒为 `False`，`weekly_enabled` 可由 `parameter_profile` 和 `data_days_used` 推导。
- **问题**：`user_prophet_models` 中 3 个字段与当前固定预测策略耦合，其中 2 个在现有代码下为常量，1 个可由已有训练上下文重建；保存字段数量超过加载模型实际必需字段。
- **建议**：先抽出 `derive_7_day_seasonality(parameter_profile, data_days_used)`，加载复用模型时从持久化元数据推导 seasonality；迁移中删除 `aggregation_mode` 和 `monthly_enabled`，`weekly_enabled` 是否删除由设计阶段再确认兼容性。
- **建议映射的方法**：M-L2-03（Extract Variable / Replace Temp with Query 提取变量 / 以查询取代临时变量）
- **风险**：中（会改变训练说明 metadata 的来源，需要确保复用旧模型时展示信息不漂移）
- **验证**：AI 自证（为 7 天 seasonality 派生补单测；跑 `uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_compact_prediction_mapper.py`）
- **范围**：约 70 行 / 5 文件
