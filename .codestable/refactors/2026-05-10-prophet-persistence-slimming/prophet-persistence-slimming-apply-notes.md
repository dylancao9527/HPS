---
doc_type: refactor-apply-notes
refactor: 2026-05-10-prophet-persistence-slimming
---

# prophet-persistence-slimming apply notes

## 步骤 1: 补强目标形态刻画测试

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/tests/prediction/test_prophet_gateway.py`
  - `backend/tests/prediction/test_forecast_period_policy.py`
  - `backend/tests/prediction/test_prediction_repository_boundaries.py`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py::test_prophet_model_store_uses_fixed_7_day_free_storage_keys tests/prediction/test_prophet_gateway.py::test_predict_bp_trend_reuses_loaded_active_model tests/prediction/test_prophet_gateway.py::test_predict_bp_trend_trains_and_caches_when_reuse_disabled -q` 通过，3 passed
  - `cd backend && uv run pytest tests/prediction/test_forecast_period_policy.py -q` 通过，2 passed
- 偏离: 用户追加确认 #3，范围从原来的 #1 #2 扩大到强精简模型表。

## 步骤 2: 简化 Prophet 资产路径与持久化调用

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/prediction/infrastructure/prophet_model_store.py`
  - `backend/prediction/infrastructure/prophet_gateway.py`
  - `backend/prediction/infrastructure/prophet_model_repository.py`
  - `backend/prediction/infrastructure/repositories.py`
  - `backend/prediction/infrastructure/prophet_trainer.py`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_forecast_period_policy.py tests/prediction/test_prediction_repository_boundaries.py -q` 通过，33 passed
- 偏离: 无

## 步骤 3: 精简 user_prophet_models 表和迁移

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/models/user_prophet_model.py`
  - `backend/prediction/infrastructure/prophet_model_repository.py`
  - `backend/migrations/versions/75f5fe8065f4_initial_schema.py`
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_forecast_period_policy.py -q` 通过，2 passed
  - `cd backend && uv run python -m py_compile migrations/versions/75f5fe8065f4_initial_schema.py` 通过
- 偏离: upgrade 按用户确认先删除旧 `user_prophet_models` 行，再删除冗余字段和索引；后续预测重新生成模型资产。

## 步骤 4: 删除旧资产并同步文档

- 完成时间: 2026-05-10
- 改动文件:
  - `backend/prediction/infrastructure/prophet_asset_maintenance.py`
  - `.codestable/architecture/ARCHITECTURE.md`
  - `.codestable/refactors/2026-05-10-prophet-persistence-slimming/prophet-persistence-slimming-scan.md`
  - `.codestable/refactors/2026-05-10-prophet-persistence-slimming/prophet-persistence-slimming-refactor-design.md`
  - `.codestable/refactors/2026-05-10-prophet-persistence-slimming/prophet-persistence-slimming-checklist.yaml`
- 验证结果:
  - 删除 `backend/runtime/prophet_models/user_*/fd_*`：`removed_legacy_fd_dirs=14`
  - `Get-ChildItem -Recurse backend/runtime/prophet_models` 无剩余文件输出
- 偏离: 无

## 步骤 5: 整体验证

- 完成时间: 2026-05-10
- 改动文件: 全部本次改动文件
- 验证结果:
  - `cd backend && uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_forecast_period_policy.py tests/prediction/test_prediction_repository_boundaries.py -q` 通过，33 passed
  - `cd backend && uv run pytest -q` 通过，197 passed
  - `cd backend && uv run python -m py_compile migrations/versions/75f5fe8065f4_initial_schema.py` 通过
  - `python .codestable/tools/validate-yaml.py --dir .codestable/refactors/2026-05-10-prophet-persistence-slimming` 通过，4 passed
  - `rg -n "UserProphetModel\\.forecast_days|fd_\\{|fd_7" backend/prediction backend/models --glob "*.py"` 无匹配
  - 用户要求删除旧迁移链后，重建本地 `hypertension` 空库并执行 `cd backend && uv run flask db upgrade`，从空库完整迁移到 `75f5fe8065f4 (head)`
- 偏离: 无
