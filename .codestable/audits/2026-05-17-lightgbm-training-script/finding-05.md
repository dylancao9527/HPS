---
doc_type: audit-finding
audit: 2026-05-17-lightgbm-training-script
finding_id: "bug-05"
nature: bug
severity: P1
confidence: medium
suggested_action: cs-issue
status: open
---

# Finding 05：默认训练直接覆盖生产模型且非原子写入

## 速答

不带 `--run-name` 或 `--no-promote` 时，训练默认写入 `backend/ml_models/` 和 canonical 报告；保存时先写模型再写配置，没有临时目录、manifest、smoke load 或原子替换，存在误覆盖和半写入风险。

## 关键证据

- `backend/scripts/train_models.py:129` - 只有传入 `--run-name` 时才创建 named artifact dir。
- `backend/scripts/train_models.py:130` - `promote = args.promote or (artifact_dir is None and not args.no_promote)`，默认无 artifact dir 时会 promote。
- `backend/training/pipeline.py:390` - `if promote or saved_artifact_dir is None:` 会保存到默认生产模型目录。
- `backend/training/reporting.py:267` - `save_final_model()` 解析默认目标目录为 `MODELS_DIR`。
- `backend/training/reporting.py:270` - 先 `model.save_model(str(model_path))` 写 `lgbm_model.txt`。
- `backend/training/reporting.py:292` - 随后才写 `model_config.json`，中间没有原子 swap 或一致性校验。
- `backend/prediction/infrastructure/model_registry.py:66` - 线上注册表分别懒加载模型文件与配置文件，没有模型/配置 manifest 版本绑定。

## 影响

一次普通本地训练就可能覆盖生产模型资产；如果保存过程中异常中断，可能留下新模型配旧配置或旧模型配新配置。即使 feature contract 没变，`classification_threshold`、`dataset_hash`、`training_code_version` 与实际模型也可能不一致，影响预测结果追踪和回滚。

## 修复方向

把训练产物发布拆成 candidate run 和 promote 两阶段：默认写 `backend/ml_runs/<timestamp>-...`；显式 promote 时先写临时目录，完成 `model_config.json` 校验、Booster 加载、特征顺序 smoke predict 和 manifest 生成后，再原子替换生产目录，并保留上一版备份。

## 建议动作

`cs-issue`，因为这是模型资产发布安全问题，应优先补 "promote 前后模型/配置一致" 的集成测试或脚本级 smoke check。
