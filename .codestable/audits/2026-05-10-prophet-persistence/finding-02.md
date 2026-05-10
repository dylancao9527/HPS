---
doc_type: audit-finding
audit: 2026-05-10-prophet-persistence
finding_id: "bug-02"
nature: bug
severity: P1
confidence: medium
suggested_action: cs-issue
status: fixed
---

# Finding 02：并发预测可能留下多个 active Prophet 模型元数据

## 速答

`save_user_prophet_model()` 用“先 update 旧 active，再 insert 新 active”的两步写法，但数据库没有约束保证同一用户只能有一个 active 模型，并发预测时可能留下多条 `is_active=True`。

## 关键证据

- `backend/models/user_prophet_model.py:8` — 当前索引 `ix_user_prophet_models_active_slot_trained` 是普通索引，不是唯一约束。
- `backend/models/user_prophet_model.py:24` — `is_active` 只是普通布尔列，默认 True。
- `backend/prediction/infrastructure/prophet_model_repository.py:21` — 保存时先把当前 active 行 update 为 False。
- `backend/prediction/infrastructure/prophet_model_repository.py:26` — 随后新建一条 `is_active=True` 行。
- `backend/prediction/infrastructure/prophet_model_repository.py:36` — commit 只包住当前事务，没有数据库层唯一约束兜底。

## 影响

正常串行请求下不会暴露；但同一用户两个预测请求同时重训时，两个事务都可能认为旧 active 已处理并各自插入新 active。之后 `get_active_prophet_model()` 会按时间取一条，但另一条仍被当作 active，清理逻辑只清 inactive，元数据语义会漂移。

## 修复方向

给 active 模型建立数据库层约束或引入显式事务锁；MySQL 可考虑生成列 / 复合唯一策略，或在保存时对用户模型槽位加锁。

## 建议动作

`cs-issue`，因为这是并发一致性 bug，需要先设计可在 MySQL 上落地的约束或锁方案。
