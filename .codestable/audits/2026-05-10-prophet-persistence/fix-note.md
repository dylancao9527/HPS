---
doc_type: audit-fix-note
audit: 2026-05-10-prophet-persistence
created: 2026-05-11
status: fixed
---

# prophet-persistence 审计修复记录

## 修复内容

- Finding 01：初始迁移 downgrade 改为按依赖顺序直接 drop table，不再手动 drop 外键支撑索引。
- Finding 02：`save_user_prophet_model()` 在保存前对 `users.id` 执行 `SELECT ... FOR UPDATE`，序列化同一用户的 active 模型切换；不新增生成列，保持 `user_prophet_models` 表精简。
- Finding 03：`LocalProphetModelStore` 对 `storage_key` 做空值、绝对路径、盘符、`.` / `..` 段和 root 边界校验。
- Finding 04：新增 domain 分页策略，预测历史和治理列表统一将 `per_page` 限制到最大 100。
- Finding 05：`AGGREGATION_MODE` 上移到 domain run key policy，application 层不再从 infrastructure import 常量。

## 验证

- `uv run pytest tests\prediction -q`
- `uv run pytest tests\routes\test_predictions_route_use_cases.py tests\services\test_prediction_governance_service.py tests\migrations\test_initial_schema_migration.py -q`
- 临时 MySQL 库执行 `uv run flask db upgrade` + `uv run flask db downgrade base`
- `uv run pytest -q`
- `uv run flask db current`
