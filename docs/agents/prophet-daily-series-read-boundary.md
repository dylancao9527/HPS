# Prophet 每日血压序列读取边界

日期：2026-05-07

## 当前决策

- Prophet 训练输入的领域单位是 **每日血压序列**，不是原始单次血压记录。
- 本阶段已将 `_load_daily_records()` 改为数据库按日聚合投影：
  - `date(recorded_at)`
  - `avg(systolic_bp)`
  - `avg(diastolic_bp)`
  - `count(*) as measurements`
- Python 侧不再加载用户全量原始 BP records 后再 groupby。

## 保留语义

- `total_history_days` 仍表示用户历史中可用于 Prophet 的自然日总数。
- `data_days_used` 仍由 `PROPHET_MAX_TRAIN_DAYS` 裁剪后的每日序列长度决定。
- `history_window_capped` 仍在 `total_history_days > PROPHET_MAX_TRAIN_DAYS` 时为 true。
- `new_data_days_since_training` 仍基于每日序列日期与 `trained_until` 比较。
- `data_signature` 仍基于实际进入训练窗口的每日血压序列生成。

## 后续可选优化

如果真实性能数据证明“全量每日序列”仍然过大，可进一步拆成三类查询：

1. `count(distinct date(recorded_at))` 计算 `total_history_days`。
2. 最近 `PROPHET_MAX_TRAIN_DAYS` 个自然日的每日聚合序列用于训练和 `data_signature`。
3. `count(distinct date(recorded_at)) where date(recorded_at) > trained_until` 计算 `new_data_days_since_training`。

该优化需要调整 `build_training_context()` 的入参，让它接收 total metrics 与 capped daily frame，避免再次依赖完整每日序列。

## 暂不引入每日序列表

现阶段不建议新增物化 **每日血压序列** 表：

- 当前查询已经从“原始记录全量加载”降为“数据库每日聚合投影”。
- 物化表会引入写入同步、回填、修复和一致性成本。
- 若后续需要物化表，应先记录真实慢查询证据，并单独形成 ADR 与迁移计划。

## 索引依赖

阶段 15 候选索引 `bp_records(user_id, recorded_at)` 能支持按用户读取、按时间排序和按日期聚合的主路径。该索引仍需维护者确认后单独实施迁移。
