---
doc_type: audit-fix-note
audit: 2026-05-11-training-frontend
created: 2026-05-11
status: fixed
---

# training-frontend 审计修复记录

## 修复范围

- Finding 01：历史页批量删除只提交当前可见记录，分页、筛选变化时清空选择。
- Finding 02：`TrainingConfig.max_boost_rounds` 和 `early_stopping_rounds` 透传到 LightGBMTunerCV 调参阶段。
- Finding 03：`dataset_hash` 在 hash 前按稳定列排序，不再受训练 seed 的 shuffle 顺序影响。
- Finding 04：本地模拟邮箱验证码 UI 增加 `DEV` / `VITE_ENABLE_LOCAL_MOCK_EMAIL_UI` 闸门。
- Finding 05：`ProfileForm` 状态与动作拆到 section hooks，组件 shell 只负责组合布局。

## 验证

- `cd backend && uv run pytest tests\training -q`：31 passed
- `cd backend && uv run pytest -q`：210 passed
- `cd frontend && pnpm vitest run --reporter verbose`：21 files / 40 tests passed
- `cd frontend && pnpm run typecheck`：passed
- `cd frontend && pnpm run lint`：passed
- `cd frontend && pnpm run build`：passed
- Chrome headless 浏览器验证：`/history` 翻页后批量删除请求体为 `{"ids":[2]}`。
