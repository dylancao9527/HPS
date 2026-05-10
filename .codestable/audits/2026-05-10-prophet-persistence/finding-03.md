---
doc_type: audit-finding
audit: 2026-05-10-prophet-persistence
finding_id: "security-03"
nature: security
severity: P2
confidence: medium
suggested_action: cs-issue
status: fixed
---

# Finding 03：Prophet storage_key 未做路径边界校验

## 速答

`LocalProphetModelStore` 直接把 `storage_key` 拼到 root 后面，没有校验最终路径仍在 Prophet 模型目录内；如果数据库里出现异常 storage key，读写删都可能越界。

## 关键证据

- `backend/prediction/infrastructure/prophet_model_store.py:36` — `_bundle_dir()` 直接返回 `self.root / storage_key`。
- `backend/prediction/infrastructure/prophet_model_store.py:50` — `read_bundle()` 用该路径读取 `sys_model.pkl` / `dia_model.pkl`。
- `backend/prediction/infrastructure/prophet_model_store.py:62` — `delete_bundle()` 用同一路径执行 `shutil.rmtree()`。
- `backend/prediction/infrastructure/prophet_model_repository.py:39` — 清理命令会从数据库列出所有 `storage_key`，再交给 store 删除。

## 影响

当前写入路径由 `build_storage_key()` 生成，外部用户无法直接传入 storage key，所以不是 P0/P1。风险在于数据库手工修复、历史脏数据、未来接口改动或测试脚本写入异常 key 时，文件操作缺少最后一道边界保护。

## 修复方向

在 `_bundle_dir()` 中 resolve root 和目标路径，拒绝 `..`、绝对路径、空 key，以及任何不在 root 下的路径；同时用单测覆盖 read/delete/write。

## 建议动作

`cs-issue`，因为涉及文件删除边界，应该作为安全加固定点修。
