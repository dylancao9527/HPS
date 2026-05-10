---
doc_type: audit-finding
audit: 2026-05-11-routes-services-scripts
finding_id: "performance-05"
nature: performance
severity: P2
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 05：多个列表/趋势端点未限制 per_page/limit 上限

## 速答

预测历史和治理列表已有 `MAX_PAGE_SIZE=100` 的分页策略，但 `bp-records`、管理员用户列表和 profile 预测趋势仍直接使用请求参数，客户端可请求超大结果集。

## 关键证据

- `backend/routes/bp_records.py:30` — `page` 直接从 query string 读取。
- `backend/routes/bp_records.py:31` — `per_page` 直接从 query string 读取，没有上限。
- `backend/services/bp_record_service.py:35` — 血压记录列表直接把该 `per_page` 传给 `paginate()`。
- `backend/routes/admin.py:48` — 管理员用户列表直接读取 `page`。
- `backend/routes/admin.py:49` — 管理员用户列表直接读取 `per_page`，没有统一限幅。
- `backend/services/admin_service.py:10` — `AdminUserService.list_users()` 直接将 `per_page` 传给 `paginate()`。
- `backend/routes/profile.py:51` — `prediction-trend` 的 `limit` 直接来自请求参数。
- `backend/prediction/infrastructure/prediction_record_repository.py:87` — 趋势查询直接使用 `.limit(limit)`。
- `backend/prediction/domain/pagination_policy.py:4` — 预测模块已有 `MAX_PAGE_SIZE = 100`，说明项目内已有可复用边界。

## 影响

普通用户可用超大的 `per_page` 或 `limit` 拉取大量血压/预测趋势数据，管理员用户列表也可被请求放大。数据量不大时影响有限，但长期使用后会增加数据库压力、响应体大小和前端渲染成本；非法负数或极端值还可能触发数据库方言差异。

## 修复方向

把 `normalize_page()` / `normalize_per_page()` 抽到可复用位置或在这些服务中复用同等策略；`limit` 也应设置默认值、最小值和最大值。

## 建议动作

`cs-issue`，因为这是接口输入边界问题，适合补几个 query 参数归一化测试。

## 修复结果

已修复。血压记录列表、管理员用户列表和个人预测趋势统一复用分页策略，将非法页码归一到默认值，并把 `per_page` / `limit` 上限限制为 100。
