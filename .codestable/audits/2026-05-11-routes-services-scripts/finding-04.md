---
doc_type: audit-finding
audit: 2026-05-11-routes-services-scripts
finding_id: "bug-04"
nature: bug
severity: P2
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 04：血压记录的非法 recorded_at 会被静默替换为当前时间

## 速答

新增血压记录时，如果客户端提交的 `recorded_at` 格式非法，服务端不会报错，而是把记录时间替换成当前时间，可能污染用户趋势和周报。

## 关键证据

- `backend/routes/bp_records.py:39` — 新增记录直接把请求 JSON 传给 `BPRecordService.create_record()`。
- `backend/services/bp_record_service.py:62` — `create_record()` 使用 `_parse_recorded_at(data.get("recorded_at"))` 得到保存时间。
- `backend/services/bp_record_service.py:96` — `_parse_recorded_at()` 开始解析客户端传入的时间字符串。
- `backend/services/bp_record_service.py:103` — `fromisoformat()` 抛 `ValueError` 时进入异常分支。
- `backend/services/bp_record_service.py:104` — 异常分支将 `recorded_at` 设置为 `utc_now_naive()`，没有向用户返回 400。

## 影响

用户或前端一旦传入拼写错误、时区格式不兼容或空格异常的时间，系统会保存为“现在”。这会影响血压历史顺序、每日聚合、Prophet 训练边界、健康任务和周报趋势，且用户很难发现根因。

## 修复方向

非法 `recorded_at` 应返回 400；只有未传 `recorded_at` 时才默认使用当前时间。补一个路由或服务测试覆盖非法日期。

## 建议动作

`cs-issue`，因为这是清晰的输入校验 bug，修复范围可控制在血压记录服务与测试。

## 修复结果

已修复。`recorded_at` 未传时才使用当前时间；只要客户端传入非法日期格式，新增血压记录接口返回 400，避免静默写入错误时间。
