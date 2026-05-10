---
doc_type: audit-finding
audit: 2026-05-10-prophet-persistence
finding_id: "performance-04"
nature: performance
severity: P2
confidence: medium
suggested_action: cs-refactor
status: fixed
---

# Finding 04：预测历史和治理分页缺少 per_page 上限

## 速答

预测历史接口和治理查询只处理默认值/正数，没有设置最大 `per_page`，调用方可以请求很大的页大小，触发大量 JSON payload 组装。

## 关键证据

- `backend/routes/predictions.py:86` — `page` 直接来自 query string。
- `backend/routes/predictions.py:87` — `per_page` 直接来自 query string，未限制上限。
- `backend/prediction/schemas/commands.py:17` — `GetPredictionHistoryQuery` 只是 dataclass，没有 `__post_init__` 做范围归一化。
- `backend/prediction/infrastructure/prediction_record_repository.py:36` — repository 直接把 `per_page` 传入 SQLAlchemy paginate，并逐条 assemble 完整预测 payload。
- `backend/prediction/infrastructure/prediction_governance_read_model.py:47` — governance 查询只把非正数恢复为 20；正的大数没有 cap。
- `backend/prediction/infrastructure/prediction_governance_read_model.py:438` — export 路径会 `query.all()` 后再投影所有记录。

## 影响

数据量小时不明显；预测记录增多后，大页请求会放大数据库读取和 JSON 反序列化/组装成本。管理员导出本来可以全量，但普通列表和治理分页应有上限，避免误操作或简单脚本把服务打满。

## 修复方向

集中定义分页策略，例如默认值和最大值，普通列表 clamp 到固定上限；导出保留全量语义但使用流式/分批读取。

## 建议动作

`cs-refactor`，因为主要是边界策略和重复分页归一化抽取，不需要改变预测业务语义。
