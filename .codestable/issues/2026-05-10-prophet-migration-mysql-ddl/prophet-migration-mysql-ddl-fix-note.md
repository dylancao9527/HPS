---
doc_type: issue-fix
issue: 2026-05-10-prophet-migration-mysql-ddl
status: fixed
severity: medium
tags:
  - backend
  - migration
  - mysql
---

# prophet-migration-mysql-ddl fix note

## 问题

执行 `cd backend && uv run flask db upgrade` 升级 `3d7a1b9c0e2f_slim_prophet_model_persistence.py` 时，MySQL 报错：

- `Cannot drop index 'ix_user_prophet_models_user_id': needed in a foreign key constraint`
- 后续修正后又暴露 `Check constraint ... is not found in the table`

## 根因

- `user_prophet_models.user_id` 有外键指向 `users.id`。MySQL 需要保留一个可用于外键检查的 `user_id` 索引，迁移不能把 `ix_user_prophet_models_user_id` 当作普通冗余索引删除。
- Alembic batch 模式在项目命名约定下删除 check constraint 时会对约束名再套一层前缀，导致实际执行的 drop constraint 名称和 MySQL 中真实约束名不一致。

## 修复

- 保留 `ix_user_prophet_models_user_id`，ORM 也恢复 `user_id index=True`，测试断言同步为保留该外键支撑索引。
- 迁移中使用 inspector 确认真正存在的 check constraint 名称，并通过直接 `ALTER TABLE ... DROP CHECK ...` 删除，避免 batch 命名约定二次改名。

## 验证

- `cd backend && uv run pytest tests/prediction/test_forecast_period_policy.py tests/prediction/test_prophet_gateway.py tests/prediction/test_prediction_repository_boundaries.py -q` 通过，33 passed。
- 用户后续要求删除旧迁移链，已重建为 `75f5fe8065f4_initial_schema.py` 单文件初始化迁移。
- `cd backend && uv run python -m py_compile migrations/versions/75f5fe8065f4_initial_schema.py` 通过。
- 删除并重建 `hypertension` 数据库后，`cd backend && uv run flask db upgrade` 从空库完整迁移到 `75f5fe8065f4 (head)`。
- 重建后 `user_prophet_models` 只保留模型资产字段，并有两个索引：`ix_user_prophet_models_active_slot_trained` 和 `ix_user_prophet_models_user_id`。
