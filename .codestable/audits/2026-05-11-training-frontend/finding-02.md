---
doc_type: audit-finding
audit: 2026-05-11-training-frontend
finding_id: "bug-02"
nature: bug
severity: P1
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 02：训练参数文件无法控制 LightGBMTunerCV 的轮数与早停

## 速答

`TrainingConfig` 支持 `max_boost_rounds` 和 `early_stopping_rounds`，最终训练阶段也使用它们，但 LightGBMTunerCV 调参阶段仍固定读取模块常量，导致参数文件无法完整控制训练流程。

## 关键证据

- `backend/training/pipeline.py:253` — 主流程进入“官方调优”阶段。
- `backend/training/pipeline.py:254` — 调用 `tuning_strategy.tune(...)` 时只传入 `learning_rate=config.learning_rate`，没有传入 `config.max_boost_rounds` 或 `config.early_stopping_rounds`。
- `backend/training/trainer.py:417` — `tune_lightgbm_with_tuner_cv()` 的函数签名没有接收轮数和早停参数。
- `backend/training/trainer.py:457` — `LightGBMTunerCV` 固定使用 `num_boost_round=MAX_BOOST_ROUNDS`。
- `backend/training/trainer.py:459` — early stopping 固定使用 `EARLY_STOPPING_ROUNDS`。
- `backend/training/pipeline.py:55` — 相比之下，最终训练阶段已经把 `config.max_boost_rounds` 传给 `LightGBMTrainer`，说明调参阶段和最终阶段口径不一致。

## 影响

用户通过 `scripts/train_models.py --params experiment.json` 调整 `max_boost_rounds` 或 `early_stopping_rounds` 时，只影响最终训练，不影响官方调参。对照实验会出现“参数文件看似生效、但最耗时且最关键的调参阶段仍走默认值”的偏差，影响训练耗时、最优参数和论文实验可复现性。

## 修复方向

把轮数和早停作为 `TuningStrategy.tune()` 参数或新增配置对象参数，让 LightGBMTunerCV 与最终训练阶段使用同一个 `TrainingConfig`。

## 建议动作

`cs-issue`，因为这是参数控制语义和实验复现性的功能 bug。
