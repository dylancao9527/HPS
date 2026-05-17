---
doc_type: audit-finding
audit: 2026-05-17-lightgbm-training-script
finding_id: "bug-01"
nature: bug
severity: P1
confidence: high
suggested_action: cs-issue
status: open
---

# Finding 01：阈值验证集在调参阶段已经参与 CV

## 速答

训练报告声称阈值集与 early stopping 隔离，但当前流程先用完整 `X_train` 做 LightGBMTunerCV，再在最终训练阶段内部切出阈值集，导致阈值集没有从模型选择阶段隔离。

## 关键证据

- `backend/training/pipeline.py:317` - `run_training()` 先进入 "官方调优" 阶段。
- `backend/training/pipeline.py:318` - `tuning_strategy.tune(X_train, y_train, ...)` 直接使用完整训练集做 CV 调参。
- `backend/training/pipeline.py:107` - `_train_final_cycle()` 在调参之后才创建 `LightGBMTrainer(...).with_threshold_isolation(...)`。
- `backend/training/trainer.py:284` - 阈值集只在 `LightGBMTrainer.build_data()` 内部从 `X_train` 切出，发生在最终训练周期里。
- `backend/training/reporting.py:143` - 报告输出 `阈值集与 early stopping 隔离`，但这里的隔离只覆盖最终训练/早停，不覆盖前面的 CV 调参。

## 影响

最终测试集指标仍然有独立 test split，因此不是测试集泄漏；但阈值验证集参与了超参数选择，后续又用于分类阈值搜索，会让阈值策略的独立性被高估。对于论文实验、模型报告和后续阈值治理，这会造成 "threshold holdout" 语义不准确。

## 修复方向

在 `run_training()` 层先从训练集切出 `X_threshold/y_threshold`，LightGBMTunerCV 只接收剩余的 model-selection pool；最终模型参数冻结后，再用真正未参与调参的 threshold holdout 搜索阈值。

## 建议动作

`cs-issue`，因为这是实验隔离语义和训练评估可信度问题，适合补流程测试验证 tuner 输入不包含 threshold holdout。
