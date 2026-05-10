---
doc_type: audit-finding
audit: 2026-05-11-training-frontend
finding_id: "bug-01"
nature: bug
severity: P1
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 01：预测历史批量删除会带上当前页不可见的旧选中项

## 速答

`HistoryPage` 的 `selected` 是跨分页和筛选保留的全局集合，但批量删除直接提交整个集合，用户可能删除当前列表不可见的历史预测记录。

## 关键证据

- `frontend/src/pages/HistoryPage.tsx:20` — `selected` 只用一个 `Set` 维护，没有按当前页或筛选条件隔离。
- `frontend/src/pages/HistoryPage.tsx:65` — 单条 toggle 基于旧 `selected` 增删，切换分页或日期筛选时没有清理。
- `frontend/src/pages/HistoryPage.tsx:75` — `allSelected` 只判断当前 `records`，但不移除已经不在当前页的 selected id。
- `frontend/src/pages/HistoryPage.tsx:92` — 批量删除确认使用 `selected.size`，其中可能包含当前不可见记录。
- `frontend/src/pages/HistoryPage.tsx:102` — `batchDeletePredictions([...selected])` 直接提交全部 selected id。

## 影响

普通用户在第 1 页选中记录后切到第 2 页或调整日期筛选，再执行批量删除时，之前不可见的选中记录也会被删除。因为删除记录是用户数据破坏性操作，这个问题应该按 P1 处理。

## 修复方向

分页、筛选变化时清理选中项，或像管理员用户表一样计算 `visibleSelected`，批量删除只提交当前视图可见记录。

## 建议动作

`cs-issue`，因为这是具体可触发的数据删除边界 bug，需要补交互回归测试。
