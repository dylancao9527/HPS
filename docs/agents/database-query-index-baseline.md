# 三期数据库查询基线与索引方案

日期：2026-05-07

> 历史基线：本文记录 ADR-0007 前的多表预测存储索引分析。当前预测历史已收束到 `prediction_records` 紧凑记录，旧的 Prophet/预测明细表名只作为历史上下文保留。

## 执行边界

- 本文只记录 schema 差异、查询基线、候选索引和回滚策略。
- 未新增 Alembic 迁移脚本。
- 未修改生产配置。
- 本地未连接真实 MySQL 8 实例执行 `EXPLAIN ANALYZE`；基线来自 ORM 查询、Alembic 迁移和 `database/hypertension.sql` dump 的静态对照。接入真实库后应按本文 SQL 模板补充真实 rows / filtered / Extra。

## Schema 对照

| 对象 | ORM 当前结构 | Alembic 当前结构 | `database/hypertension.sql` | 差异与处理 |
|---|---|---|---|---|
| `users` | 普通用户账户信息，无 `role` | 初始迁移有 `role`，`f4a9d2c6b8e1` 删除 | 仍有 `role` | dump 落后于迁移，应在后续单独刷新 dump。 |
| `admin_users` | 独立管理员账户表 | `f4a9d2c6b8e1` 创建 | 缺失 | dump 落后；管理员不应关联健康档案。 |
| `prophet_predictions.forecast_days` | check 固定 7 天 | `8b9c2d1e4f73` 创建 check | 无 check | dump 落后；保持 ADR-0004。 |
| `user_prophet_models.forecast_days` | check 固定 7 天 | `8b9c2d1e4f73` 创建 check | 无 check | dump 落后；保持 ADR-0004。 |
| 预测明细表 | 规范化存储 6 张明细表 | 与 ORM 对齐 | 基本对齐 | 这是 ADR-0007 前的历史基线；当前预测历史已收束到 `prediction_records` 紧凑记录。 |

## 当前索引基线

| 表 | 当前主要索引 | 观察 |
|---|---|---|
| `bp_records` | `ix_bp_records_user_id(user_id)` | 高频查询通常还按 `recorded_at` 排序或范围过滤，单列索引会产生额外排序/回表。 |
| `prediction_records` | `ix_prediction_records_user_id(user_id)`，FK 自动索引 `prophet_prediction_id` | 用户历史按 `created_at` 倒序分页，治理按 `risk_level`/`created_at` 过滤排序，均缺复合索引。 |
| `prophet_predictions` | `ix_prophet_predictions_user_id(user_id)`，`ix_prophet_predictions_cache_key(cache_key)` | Prophet 历史列表和保留上限清理按 `user_id + created_at` 排序。 |
| `user_prophet_models` | 单列 `user_id`、`is_active`、`model_version`、`data_signature` | 活跃模型读取按 `user_id + forecast_days + is_active` 过滤，再按 `trained_at,id` 倒序取 1。 |
| `prediction_training_meta` | PK `prophet_prediction_id` | 治理置信度筛选会按 `confidence_level` 过滤后关联预测主记录，缺置信度前缀索引。 |
| `prophet_forecast_points` | unique `(prophet_prediction_id, forecast_day)` 和单列 FK | 读取预测点已由 unique 复合索引覆盖，单列 FK 索引可评估是否重复。 |

## 高频查询与 EXPLAIN 模板

### 血压记录列表

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM bp_records
WHERE user_id = ?
ORDER BY recorded_at DESC
LIMIT ? OFFSET ?;
```

当前预期：走 `ix_bp_records_user_id` 后 filesort。

目标索引：`bp_records(user_id, recorded_at)`。

### 最新血压

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM bp_records
WHERE user_id = ?
ORDER BY recorded_at DESC
LIMIT 1;
```

目标索引：同 `bp_records(user_id, recorded_at)`，可反向扫描直接取最新记录。

### 预测历史

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM prediction_records
WHERE user_id = ?
  AND created_at >= ?
  AND created_at < ?
ORDER BY created_at DESC
LIMIT ? OFFSET ?;
```

当前预期：走 `ix_prediction_records_user_id` 后对用户记录排序。

目标索引：`prediction_records(user_id, created_at)`。

### Prophet 历史与保留上限清理

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM prophet_predictions
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT ?;
```

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM prophet_predictions
WHERE user_id = ?
ORDER BY created_at ASC
LIMIT ?;
```

目标索引：`prophet_predictions(user_id, created_at)`。

### 活跃 Prophet 模型

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM user_prophet_models
WHERE user_id = ?
  AND forecast_days = 7
  AND is_active = 1
ORDER BY trained_at DESC, id DESC
LIMIT 1;
```

目标索引：`user_prophet_models(user_id, forecast_days, is_active, trained_at, id)`。

### 预测结果治理列表

```sql
EXPLAIN FORMAT=TREE
SELECT pr.*
FROM prediction_records pr
LEFT JOIN prediction_training_meta ptm
  ON ptm.prophet_prediction_id = pr.prophet_prediction_id
WHERE pr.risk_level = ?
  AND ptm.confidence_level = ?
ORDER BY pr.created_at DESC
LIMIT ? OFFSET ?;
```

目标索引：

- `prediction_records(risk_level, created_at)`
- `prediction_training_meta(confidence_level, prophet_prediction_id)`

### 训练数据导出

```sql
EXPLAIN FORMAT=TREE
SELECT u.id, up.*
FROM users u
LEFT JOIN user_profiles up ON up.user_id = u.id;
```

```sql
EXPLAIN FORMAT=TREE
SELECT *
FROM bp_records
WHERE user_id IN (...)
ORDER BY user_id, recorded_at DESC;
```

目标索引：`bp_records(user_id, recorded_at)`。阶段 18 先用批量投影移除 N+1；后续有真实数据量后再评估是否需要 window function 专用索引。

## 候选迁移方案

```python
def upgrade():
    with op.batch_alter_table("bp_records") as batch_op:
        batch_op.create_index(
            "ix_bp_records_user_recorded_at",
            ["user_id", "recorded_at"],
            unique=False,
        )
    with op.batch_alter_table("prediction_records") as batch_op:
        batch_op.create_index(
            "ix_prediction_records_user_created_at",
            ["user_id", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            "ix_prediction_records_risk_created_at",
            ["risk_level", "created_at"],
            unique=False,
        )
    with op.batch_alter_table("prophet_predictions") as batch_op:
        batch_op.create_index(
            "ix_prophet_predictions_user_created_at",
            ["user_id", "created_at"],
            unique=False,
        )
    with op.batch_alter_table("user_prophet_models") as batch_op:
        batch_op.create_index(
            "ix_user_prophet_models_active_slot_trained",
            ["user_id", "forecast_days", "is_active", "trained_at", "id"],
            unique=False,
        )
    with op.batch_alter_table("prediction_training_meta") as batch_op:
        batch_op.create_index(
            "ix_prediction_training_meta_confidence_prophet",
            ["confidence_level", "prophet_prediction_id"],
            unique=False,
        )
```

## 重复索引评估

- `prophet_forecast_points(prophet_prediction_id)` 可被 unique `(prophet_prediction_id, forecast_day)` 覆盖，真实 MySQL 上确认外键约束不依赖单列索引后可考虑删除。
- `bp_records(user_id)` 可被 `(user_id, recorded_at)` 覆盖，但为降低迁移风险，建议第一轮先保留单列索引，观察写入成本后再清理。
- `prediction_records(user_id)` 可被 `(user_id, created_at)` 覆盖，同样建议第一轮保留。
- `prophet_predictions(user_id)` 可被 `(user_id, created_at)` 覆盖，同样建议第一轮保留。
- `user_prophet_models(user_id)` 可被活跃模型复合索引覆盖，但可能仍服务其他用户级扫描，先保留。
- `user_prophet_models(is_active)` 单列索引选择性较低，后续若无单独后台扫描可考虑删除。

## 回滚策略

- 每个新增索引的 downgrade 只执行对应 `drop_index`，不触碰数据。
- 索引迁移应在业务低峰执行；MySQL 8 可评估 `ALGORITHM=INPLACE` / `LOCK=NONE` 能力，但 Alembic batch 生成 SQL 前需在预发库确认。
- 若新增索引导致写入延迟不可接受，优先回滚治理侧索引 `prediction_records(risk_level, created_at)` 与 `prediction_training_meta(confidence_level, prophet_prediction_id)`，再回滚用户侧时间排序索引。

## 阶段 15 结论

1. 现有 dump 已落后于 Alembic 与 ORM，不应作为实施 schema 的唯一来源。
2. 三期后续查询优化可先改应用查询，不依赖新增索引即可减少全量扫描。
3. 复合索引迁移需要维护者再次确认后单独实施。
