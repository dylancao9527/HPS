---
doc_type: audit-finding
audit: 2026-05-10-prophet-persistence
finding_id: "arch-drift-05"
nature: arch-drift
severity: P2
confidence: high
suggested_action: cs-refactor
status: fixed
---

# Finding 05：application 层反向依赖 infrastructure 常量

## 速答

`prediction.application.prediction_run` 为了构造 run key 直接 import `prediction.infrastructure.prophet_gateway.AGGREGATION_MODE`，和架构文档中 application 层不关心底层实现细节的分层说明不一致。

## 关键证据

- `.codestable/architecture/ARCHITECTURE.md:105` — 架构定义了 prediction 的 application 层。
- `.codestable/architecture/ARCHITECTURE.md:114` — application 层职责是编排流程，不直接关心底层数据库细节和模型文件读写。
- `.codestable/architecture/ARCHITECTURE.md:127` — infrastructure 层负责数据库读写、模型序列化、文件存储和缓存。
- `backend/prediction/application/prediction_run.py:10` — application 层直接从 infrastructure 的 `prophet_gateway` import `AGGREGATION_MODE`。
- `backend/prediction/application/prediction_run.py:56` — 该常量参与 `build_prediction_run_key()`。
- `backend/prediction/infrastructure/prophet_training_context.py:9` — `AGGREGATION_MODE` 实际定义在 infrastructure 训练上下文中。

## 影响

当前只是一个常量，功能风险低。但它让 application 层知道 Prophet 训练实现细节，后续如果 aggregation mode 继续演进，run key 规则、训练上下文和 application 编排容易互相牵扯。

## 修复方向

把 aggregation mode 移到 domain 层的 run key / training policy，或让 Prophet gateway 在 `prophet_result.training_meta` 中返回并由 application 读取结果值，避免 application 反向 import infrastructure。

## 建议动作

`cs-refactor`，因为这是分层边界整理，行为应保持不变。
