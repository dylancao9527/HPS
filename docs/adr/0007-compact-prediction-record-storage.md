# 收束预测历史为紧凑预测记录存储

用户端预测摘要和预测结果治理仍然需要保存一次 7 天风险预测的趋势、输入快照、风险融合信息、置信度说明和指南型健康建议，但当前拆成 `prediction_records`、`prophet_predictions`、`prophet_forecast_points`、`prediction_training_meta`、`prediction_input_snapshots`、`prediction_fusion_meta`、`prediction_confidence_reasons` 和 `prediction_recommendations` 八张表，导致数据库结构过散、迁移维护成本偏高。

系统改为以 `prediction_records` 作为预测记录聚合表：风险概率、风险等级、数据天数、置信度、运行模式和异常标记保留为可筛选列；血压趋势预测、输入快照、风险融合元信息、Prophet 训练说明、置信度原因和指南型健康建议保存为 JSON 载荷。`user_prophet_models` 继续只负责 Prophet 模型资产持久化，不再承担一次预测历史的明细存储。

这个决策取代 ADR-0002 的“多表规范化预测结果存储”。牺牲的是逐字段 SQL 关联查询能力；换来的是更低的数据库表数量、更集中的预测记录接口、更符合用户端摘要展示和一期预测结果治理的实际查询需求。治理页仍可按风险等级、置信度和是否异常筛选，异常类型基于预测记录载荷投影得到。
