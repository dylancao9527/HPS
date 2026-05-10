---
doc_type: refactor-design
refactor: 2026-05-10-prophet-persistence-slimming
status: approved
scope: Simplify fixed 7-day Prophet asset persistence, remove legacy path compatibility for reuse, and slim user_prophet_models to reusable asset pointers only.
summary: Implement scan #1, #2, and the later-approved #3; delete old local fd_* assets and regenerate models on demand.
---

# prophet-persistence-slimming refactor design

## 1. 本次范围

- 从 scan 勾选：#1 移除 Prophet 资产路径里的 `fd_7` 槽位；#2 移除 `user_prophet_models.forecast_days`；#3 删除固定 7 天下可推导或不再需要的 Prophet 模型元数据列。
- 用户追加确认：不做旧模型兼容；本地旧模型资产可以删除，后续预测时重新生成。
- 明确不做：不移除 API / command 层的 `forecast_days` 参数校验，因为它仍是“只允许未来 7 天”的输入契约。
- 总风险档位：中。主要风险来自数据库迁移、模型资产路径变化和模型复用元数据来源变化。

## 2. 前置依赖

- 测试覆盖：`test_prophet_gateway.py`, `test_forecast_period_policy.py`, `test_prediction_repository_boundaries.py` 覆盖 Prophet 生命周期、固定 7 天策略和仓储边界。
- 调用方搜索：确认生产持久化层不再引用 `UserProphetModel.forecast_days`、旧 `fd_7` 写入路径，且 `user_prophet_models` 不再保存可推导的训练元数据列。
- 迁移链：用户后续要求删除旧迁移链，已重建为单文件初始化迁移 `75f5fe8065f4_initial_schema.py`。
- 本地资产：删除 `backend/runtime/prophet_models/user_*/fd_*` 旧资产目录；预测流程会按新路径重新训练写入。

## 3. 执行顺序

### 步骤 1：补强目标形态刻画测试

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - `LocalProphetModelStore.build_storage_key()` 断言返回 `user_<user_id>/<model_version>/<data_signature>`。
  - `list_storage_keys()` 只返回新路径；`list_legacy_storage_keys()` 单独返回 `user_*/fd_*/*/*`，仅供清理命令删除。
  - `UserProphetModel` ORM 断言不包含 `forecast_days`, `aggregation_mode`, `data_days_used`, `total_history_days`, `history_window_capped`, `parameter_profile`, `weekly_enabled`, `monthly_enabled`。
  - 模型表索引断言保留 `ix_user_prophet_models_active_slot_trained(user_id, is_active, trained_at, id)` 和 MySQL 外键必需的 `ix_user_prophet_models_user_id(user_id)`。
- 退出信号：目标测试先失败后通过。
- 验证责任：AI 自证
- 回滚：回滚测试文件即可。

### 步骤 2：简化 Prophet 资产路径与持久化调用

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - `LocalProphetModelStore.build_storage_key()` 去掉 `forecast_days` 参数。
  - `list_storage_keys()` 只枚举新路径，不把旧 `fd_*` 路径作为可复用资产返回。
  - `_build_model_cache_key()` 去掉 `forecast_days`。
  - `_persist_user_model()` 去掉不参与持久化的 `forecast_days` 与 `seasonality` 参数，只写模型版本、数据签名、训练时间、训练截止日期和 storage key。
  - `PredictionRepository.get_active_prophet_model()` 和底层仓储接口改为仅按用户读取当前活跃模型。
- 退出信号：
  - `uv run pytest tests/prediction/test_prophet_gateway.py::test_prophet_model_store_uses_fixed_7_day_free_storage_keys -q`
  - `uv run pytest tests/prediction/test_prophet_gateway.py -q`
- 验证责任：AI 自证
- 回滚：回滚 gateway / store / repository 改动。

### 步骤 3：精简 `user_prophet_models` 表和迁移

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - ORM 只保留 `id`, `user_id`, `model_version`, `data_signature`, `trained_at`, `trained_until`, `storage_key`, `is_active`。
  - 仓储新建模型元数据时只写上述字段；失活和清理按用户维度处理。
  - 迁移 upgrade 先清空旧 `user_prophet_models` 行，再删除旧活跃索引、非外键必需的冗余单列索引、7 天 check constraint 和已移除字段，最后创建简化活跃索引。
  - 迁移 downgrade 恢复旧字段和旧索引；由于 upgrade 已清空旧行，恢复列可使用安全默认值。
- 退出信号：
  - `uv run pytest tests/prediction/test_forecast_period_policy.py -q`
  - `uv run pytest tests/prediction/test_prediction_repository_boundaries.py::test_get_active_prophet_model_delegates_to_prophet_models -q`
  - `uv run python -m py_compile migrations/versions/75f5fe8065f4_initial_schema.py`
- 验证责任：AI 自证
- 回滚：回滚 ORM、仓储和迁移；已迁移数据库通过 downgrade 恢复旧结构。

### 步骤 4：删除旧资产并同步文档

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - 删除 `backend/runtime/prophet_models/user_*/fd_*` 旧本地模型目录。
  - `prophet-assets-cleanup` 对 legacy storage key 执行删除，不再要求旧目录里必须有完整 bundle。
  - 更新 `.codestable/architecture/ARCHITECTURE.md` 的 Prophet 持久化说明。
  - 更新本 refactor 的 checklist / apply notes。
- 退出信号：
  - 旧 `fd_*` runtime 目录为空。
  - CodeStable YAML 校验通过。
  - 相关测试和全量测试通过。
- 验证责任：AI 自证
- 回滚：runtime 旧模型由预测重新生成；文档可回滚。

## 4. 风险与看点

- 旧模型资产不再复用：这是用户明确确认的取舍；新预测会按新路径重新训练并写入。
- 模型表元数据来源变化：复用模型时 seasonality 由当前训练上下文推导，不再从 `user_prophet_models` 读取。
- 预测记录不属于本次精简目标：`prediction_records.training_meta` 仍保存预测结果解释所需的训练说明。
- API 层固定 7 天校验保留：这不是持久化槽位，而是输入约束。
