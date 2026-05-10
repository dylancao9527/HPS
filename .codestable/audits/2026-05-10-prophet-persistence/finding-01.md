---
doc_type: audit-finding
audit: 2026-05-10-prophet-persistence
finding_id: "bug-01"
nature: bug
severity: P1
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 01：初始迁移 downgrade 在 MySQL 上先删外键索引会失败

## 速答

`75f5fe8065f4_initial_schema.py` 的 `downgrade()` 会先删除外键列上的索引，再删除表；MySQL 会拒绝删除仍被外键约束依赖的索引。

## 关键证据

- `backend/migrations/versions/75f5fe8065f4_initial_schema.py:140` — `user_risk_factor_profiles` 进入 batch alter，下一行先 drop `ix_user_risk_factor_profiles_user_id`，但该列仍有 `user_id -> users.id` 外键。
- `backend/migrations/versions/75f5fe8065f4_initial_schema.py:144` — `user_prophet_models` 同样先 drop `ix_user_prophet_models_user_id`，这和之前 Prophet 迁移里遇到的 MySQL 1553 错误同类。
- `backend/migrations/versions/75f5fe8065f4_initial_schema.py:153` 和 `:161` — `prediction_records`、`bp_records` 也先删 FK 支撑索引再删表。
- 已用临时库 `hypertension_audit_tmp` 验证：`flask db downgrade base` 失败，MySQL 报 `Cannot drop index 'ix_user_risk_factor_profiles_user_id': needed in a foreign key constraint`。

## 影响

从空库 upgrade 已经可用，但需要回滚、重建测试库或验证 downgrade 时会失败。影响主要是迁移链可靠性和开发/演示环境可恢复性。

## 修复方向

downgrade 中删除整张表前不要手动 drop 外键支撑索引；保留非 FK 索引 drop，或直接按依赖顺序 drop table。

## 建议动作

`cs-issue`，因为这是可复现的迁移命令失败，应该按 bug 修复并补一个 MySQL downgrade 验证记录。
