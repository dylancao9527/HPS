---
doc_type: refactor-apply-notes
refactor: 2026-05-10-prophet-persistence-slimming
---

# prophet-persistence-slimming apply notes

## 步骤 1: 补目标形态刻画测试

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/tests/prediction/test_prophet_gateway.py`
  - `backend/tests/prediction/test_forecast_period_policy.py`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py::test_prophet_model_store_uses_fixed_7_day_free_storage_keys -q` 按预期失败：`LocalProphetModelStore.build_storage_key()` 仍要求 `forecast_days`
  - `cd backend && uv run pytest tests/prediction/test_forecast_period_policy.py -q` 按预期失败：`UserProphetModel` 仍包含 `forecast_days`
- 偏离: 无

## 步骤 2: 兼容新旧 Prophet 资产路径

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/prediction/infrastructure/prophet_model_store.py`
  - `backend/prediction/infrastructure/prophet_gateway.py`
  - `backend/prediction/infrastructure/prophet_asset_maintenance.py`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py::test_prophet_model_store_uses_fixed_7_day_free_storage_keys -q` 通过
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py -q` 通过，10 passed
- 偏离: 无

## 步骤 3: 移除 user_prophet_models.forecast_days 数据库槽位

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/models/user_prophet_model.py`
  - `backend/prediction/infrastructure/prophet_gateway.py`
  - `backend/prediction/infrastructure/prophet_model_repository.py`
  - `backend/migrations/versions/3d7a1b9c0e2f_slim_prophet_model_persistence.py`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_forecast_period_policy.py -q` 通过，2 passed
  - `cd backend && uv run pytest tests/prediction/test_prediction_repository_boundaries.py::test_get_active_prophet_model_delegates_to_prophet_models -q` 通过，1 passed
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py -q` 通过，10 passed
- 偏离: 无

## 步骤 4: 同步架构说明并做整体验证

- 完成时间: 2026-05-10
- 改动文件:
  - `.codestable/architecture/ARCHITECTURE.md`
  - `.codestable/refactors/2026-05-10-prophet-persistence-slimming/prophet-persistence-slimming-checklist.yaml`
  - `.codestable/refactors/2026-05-10-prophet-persistence-slimming/prophet-persistence-slimming-refactor-design.md`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_forecast_period_policy.py tests/prediction/test_prediction_repository_boundaries.py -q` 通过，32 passed
  - `cd backend && uv run pytest -q` 通过，196 passed
  - `rg -n 'UserProphetModel\\.forecast_days|fd_\\{|fd_7' backend/prediction backend/models --glob "*.py"` 无匹配
  - `cd backend && uv run python -m py_compile migrations/versions/3d7a1b9c0e2f_slim_prophet_model_persistence.py` 通过
  - `python .codestable/tools/validate-yaml.py --file .codestable/refactors/2026-05-10-prophet-persistence-slimming/prophet-persistence-slimming-checklist.yaml --yaml-only` 通过
- 偏离: 原设计里的 grep 同时匹配到 `compact_prediction_mapper.py` 的预测记录载荷 `payload["forecast_days"]`，该字段属于保留的预测记录/API 载荷，不是 Prophet 模型资产槽位；已将验证范围收窄为 ORM 字段和 `fd_7` 路径残留。
