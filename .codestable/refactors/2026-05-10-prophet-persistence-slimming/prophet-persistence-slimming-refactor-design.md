---
doc_type: refactor-design
refactor: 2026-05-10-prophet-persistence-slimming
status: approved
scope: Simplify fixed 7-day Prophet model asset paths and user_prophet_models slot metadata without changing prediction behavior.
summary: Implement scan #1 and #2; keep scan #3 out of scope.
---

# prophet-persistence-slimming refactor design

## 1. 本次范围

- 从 scan 勾选：#1 把 Prophet 资产路径里的 `fd_7` 槽位移除；#2 移除 `user_prophet_models.forecast_days` 槽位字段。
- 明确不做：#3 删除固定 7 天下可推导的 Prophet 元数据列。原因：用户选择暂不做；本次保留 `aggregation_mode`, `weekly_enabled`, `monthly_enabled`，避免同时改变复用模型训练说明来源。
- 预估总工作量：中等，预计 2 个代码步骤 + 1 个迁移步骤 + 1 个文档同步步骤。
- 总风险档位：中。主要风险来自已有 Prophet 模型资产路径兼容和数据库迁移。

## 2. 前置依赖

- 测试覆盖：已有 `test_prophet_gateway.py`, `test_forecast_period_policy.py`, `test_prediction_repository_boundaries.py` 覆盖 Prophet 生命周期、固定 7 天策略和仓储边界。进入 apply 前补两个刻画测试：
  - `LocalProphetModelStore` 新路径不包含 `fd_7`，且 `list_storage_keys()` 同时枚举新旧路径。
  - `UserProphetModel` ORM 表结构不再包含 `forecast_days`，且活跃索引不再包含 `forecast_days`。
- 调用方搜索：apply 前后都运行 `rg -n "UserProphetModel\\.forecast_days|payload\\[\"forecast_days\"\\]|fd_\\{|fd_7|ck_user_prophet_models_forecast_days_7|ix_user_prophet_models_active_slot_trained" backend --glob "*.py"`，确认只剩兼容迁移或业务 API 层必要引用。
- 迁移链：新增迁移以当前 head `2a7f1c9d8e44` 为 `down_revision`。
- 文档同步：代码完成后更新 `.codestable/architecture/ARCHITECTURE.md` 中 Prophet 持久化路径和 `user_prophet_models` 字段描述。

## 3. 执行顺序

### 步骤 1：补目标形态刻画测试

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - 在 `backend/tests/prediction/test_prophet_gateway.py` 添加 store 级测试，直接实例化 `LocalProphetModelStore(tmp_path)`：
    - `build_storage_key(user_id=42, model_version="user-prophet-v1", data_signature="sig")` 返回 `user_42/user-prophet-v1/sig`。
    - 手动创建 `user_42/fd_7/user-prophet-v1/legacy-sig` 和 `user_42/user-prophet-v1/current-sig`，断言 `list_storage_keys()` 同时返回两条。
  - 在 `backend/tests/prediction/test_forecast_period_policy.py` 更新存储断言：
    - `PredictionRecord` 继续没有 `forecast_days`。
    - `UserProphetModel` 也没有 `forecast_days`。
    - `ix_user_prophet_models_active_slot_trained` 的列顺序为 `["user_id", "is_active", "trained_at", "id"]`。
- 退出信号：新增/修改测试先按预期失败，失败点分别指向旧 `build_storage_key()` 签名/路径和旧 ORM 字段。
- 验证责任：AI 自证
- 回滚：只回滚测试文件即可。

### 步骤 2：兼容新旧 Prophet 资产路径

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - 修改 `backend/prediction/infrastructure/prophet_model_store.py`：
    - `build_storage_key()` 去掉 `forecast_days` 参数，返回 `user_{user_id}/{model_version}/{data_signature}`。
    - `list_storage_keys()` 同时枚举 `user_*/*/*` 新路径与 `user_*/fd_*/*/*` 旧路径，去重排序；旧路径继续可被 `exists/read/delete` 原样访问。
  - 修改 `backend/prediction/infrastructure/prophet_gateway.py`：
    - `_persist_user_model()` 调用 `store.build_storage_key()` 时不再传 `forecast_days`。
    - 暂保留 `_persist_user_model(..., forecast_days, ...)` 外层签名，降低和生命周期步骤耦合的改动面；该参数只继续参与训练/预测，不进入文件路径。
  - 修改 `backend/prediction/infrastructure/prophet_asset_maintenance.py`：
    - legacy blob 回填生成新路径时不再传 `forecast_days`。
- 退出信号：
  - `uv run pytest tests/prediction/test_prophet_gateway.py::test_prophet_model_store_uses_fixed_7_day_free_storage_keys -q` 通过。
  - `uv run pytest tests/prediction/test_prophet_gateway.py -q` 通过。
- 验证责任：AI 自证
- 回滚：回滚上述 3 个文件；旧 `storage_key` 值仍可按原路径读取。

### 步骤 3：移除 `user_prophet_models.forecast_days` 数据库槽位

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - 修改 `backend/models/user_prophet_model.py`：
    - 删除 `forecast_days` Column 和对应 check constraint。
    - 将 `ix_user_prophet_models_active_slot_trained` 改为 `("user_id", "is_active", "trained_at", "id")`。
    - `to_dict()` 不再返回 `forecast_days`。
  - 修改 `backend/prediction/infrastructure/prophet_model_repository.py`：
    - `get_active_prophet_model(self, user_id, forecast_days=None)` 保留参数但查询只按 `user_id` + `is_active=True`。
    - `save_user_prophet_model()` 失活更新只按 `user_id` + `is_active=True`，新建行不再传 `forecast_days`。
    - `list_prophet_models_with_legacy_blobs()` 不再 SELECT `forecast_days`。
    - `prune_inactive_prophet_models()` 清理分组从 `(user_id, forecast_days)` 改为 `user_id`。
  - 新增迁移 `backend/migrations/versions/3d7a1b9c0e2f_slim_prophet_model_persistence.py`：
    - upgrade：删除旧活跃索引，删除 `ck_user_prophet_models_forecast_days_7`，删除 `forecast_days` 列，创建新活跃索引。
    - downgrade：恢复 `forecast_days` 非空默认值 7，恢复 7 天 check constraint，恢复旧活跃索引。
  - 修改 `backend/prediction/infrastructure/prophet_asset_maintenance.py` legacy blob 回填，适配 repository 不再返回 `forecast_days`。
- 退出信号：
  - `uv run pytest tests/prediction/test_forecast_period_policy.py -q` 通过。
  - `uv run pytest tests/prediction/test_prediction_repository_boundaries.py::test_get_active_prophet_model_delegates_to_prophet_models -q` 通过。
  - `uv run pytest tests/prediction/test_prophet_gateway.py -q` 通过。
- 验证责任：AI 自证
- 回滚：回滚 ORM、仓储和迁移文件；数据库已应用迁移时通过 downgrade 恢复列。

### 步骤 4：同步架构说明并做整体验证

- 引用方法：M-L1-01 Parallel Change 并行变更
- 具体操作：
  - 更新 `.codestable/architecture/ARCHITECTURE.md`：
    - Prophet 文件路径从 `user_<user_id>/fd_<forecast_days>/<model_version>/<data_signature>/` 改为 `user_<user_id>/<model_version>/<data_signature>/`。
    - `user_prophet_models` 字段说明移除 `forecast_days`，说明固定 7 天预测由预测周期策略保证，模型资产表按用户保存当前活跃模型。
  - 运行 grep 确认生产持久化层不再引用 `UserProphetModel.forecast_days` 和 `fd_` 新路径构造；允许历史迁移、架构历史和兼容性测试中保留旧字段/旧路径文本。
  - 运行后端相关测试和全量测试。
- 退出信号：
  - `uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_forecast_period_policy.py tests/prediction/test_prediction_repository_boundaries.py -q` 通过。
  - `uv run pytest -q` 通过。
  - `rg -n "UserProphetModel\\.forecast_days|fd_\\{|fd_7" backend/prediction backend/models --glob "*.py"` 不再出现新持久化路径或 ORM 字段残留；预测记录载荷里的 `forecast_days` 保留。
- 验证责任：AI 自证
- 回滚：回滚架构文档；如全量测试暴露非本范围问题，先汇报，不顺手扩大修复。

## 4. 风险与看点

- 旧文件资产兼容：本次不移动已有 `runtime/prophet_models/user_*/fd_7/...` 目录，只让新写入使用短路径，并让清理命令能枚举两种路径。
- 数据库迁移：需要在用户确认 design 后再动，迁移必须支持 downgrade 恢复 `forecast_days = 7`。
- API 层 7 天参数：本次不移除 `PredictCommand.forecast_days`、`GetBPDataStatusQuery.forecast_days` 或路由参数校验；这些属于用户输入契约，不是 Prophet 模型资产持久化槽位。
- #3 明确不做：`aggregation_mode`, `weekly_enabled`, `monthly_enabled` 仍留在模型表中，避免扩大元数据来源变化。
