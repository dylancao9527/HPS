---
doc_type: audit-fix-note
audit: 2026-05-17-lightgbm-training-script
created: 2026-05-17
status: fixed
---

# lightgbm-training-script 审计修复记录

## 修复范围

本次修复覆盖 `backend/training/` 训练链路、训练入口配置校验、训练数据读取校验、训练报告文案，以及对应的训练测试。未修改数据库结构、生产配置或前端代码。

## 修复内容

- Finding 01：在 `training.pipeline` 层先从 train split 中切出 `threshold_holdout`，LightGBMTunerCV、early stopping 和最终重训只使用 `model_selection_pool`；报告新增 `threshold_isolation_scope=before_tuning`。
- Finding 02：`find_best_threshold()` 的候选阈值改为最低分外侧边界、相邻分数 midpoint、最高分外侧边界，避免 `>` 比较漏掉全召回候选；同时写入 `recall_constraint_satisfied`。
- Finding 03：`TrainingConfig` 增加严格 schema、枚举、类型和范围校验，未知字段会在 `--params` 加载时失败。
- Finding 04：训练 CSV 读取增加数据质量门禁，校验 `Risk` 与二值特征必须为 0/1，连续生理指标必须在宽松合理范围内。
- Finding 05：生产模型发布改为候选目录写入 + 必要文件校验 + staging 替换，旧生产模型目录移动到 `backend/ml_models_previous` 作为回滚点；canonical report 从候选目录复制。

## 关键文件

- `backend/training/pipeline.py`
- `backend/training/metrics.py`
- `backend/training/config.py`
- `backend/training/data.py`
- `backend/training/trainer.py`
- `backend/training/reporting.py`
- `backend/tests/training/test_train_models_orchestration.py`
- `backend/tests/training/test_metrics_threshold.py`
- `backend/tests/training/test_training_data.py`
- `backend/tests/training/test_reporting.py`

## 验证

- `cd backend && uv run pytest tests\training -q`：38 passed
- `cd backend && uv run pytest`：228 passed
- `cd backend && uv run python -` 调用 `prepare_lgbm_data(random_seed=42)`：当前基础训练集 4240 行通过新增数据质量门禁

## 后续建议

- 后续如要继续增强模型发布，可以在 promote 阶段加入真实 `lightgbm.Booster` smoke load 和固定样本 predict 校验。
- 如果训练数据导出开始承载更多真实用户样本，建议把 invalid-row summary 输出成独立数据质量报告，方便管理员定位脏数据来源。
