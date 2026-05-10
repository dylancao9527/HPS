---
doc_type: audit-index
audit: 2026-05-10-prophet-persistence
scope: Backend prediction persistence, Prophet model metadata/storage, current initial migration, and prediction tests.
created: 2026-05-10
status: fixed
total_findings: 5
---

# prophet-persistence 审计报告

## 范围

本次审计范围为 `backend/prediction/`、`backend/models/user_prophet_model.py`、`backend/migrations/` 以及 `backend/tests/prediction/` 中和预测持久化、Prophet 模型复用、迁移初始化相关的代码。对照了 `.codestable/architecture/ARCHITECTURE.md` 中 prediction 分层与 Prophet 持久化说明。

## 总评

共发现 5 条问题：P1 2 条、P2 3 条；性质分布为 bug 2 条、security 1 条、performance 1 条、arch-drift 1 条。最值得优先处理的是新初始化迁移的 MySQL downgrade 失败，以及并发预测下 `user_prophet_models` 可能留下多个 active 模型资产。整体看，7 天固定和 Prophet 模型表精简方向已经对齐，但数据库约束、文件路径边界和分层依赖还有几处需要收紧。

## 发现清单

| # | 性质 | 严重度 | 置信度 | 标题 | 文件 |
|---|---|---|---|---|---|
| 1 | bug | P1 | high | 初始迁移 downgrade 在 MySQL 上先删外键索引会失败 | [finding-01.md](finding-01.md) |
| 2 | bug | P1 | medium | 并发预测可能留下多个 active Prophet 模型元数据 | [finding-02.md](finding-02.md) |
| 3 | security | P2 | medium | Prophet storage_key 未做路径边界校验 | [finding-03.md](finding-03.md) |
| 4 | performance | P2 | medium | 预测历史和治理分页缺少 per_page 上限 | [finding-04.md](finding-04.md) |
| 5 | arch-drift | P2 | high | application 层反向依赖 infrastructure 常量 | [finding-05.md](finding-05.md) |

## 按维度分布

| 性质 | P0 | P1 | P2 | 合计 |
|---|---|---|---|---|
| bug | 0 | 2 | 0 | 2 |
| security | 0 | 0 | 1 | 1 |
| performance | 0 | 0 | 1 | 1 |
| maintainability | 0 | 0 | 0 | 0 |
| arch-drift | 0 | 0 | 1 | 1 |
| **合计** | **0** | **2** | **3** | **5** |

## 下一步建议

- **已修复**：5 条 finding 已全部处理，见 [fix-note.md](fix-note.md)。
- **暂不建议扩大范围**：本轮只覆盖 prediction / Prophet persistence；认证、管理员服务和前端交互可另开专项审计。
