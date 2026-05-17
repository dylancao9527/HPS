---
doc_type: trick
type: technique
date: "2026-05-17"
slug: lightgbm-safe-experiment-promotion
topic: 用 run 目录先保存 LightGBM 对照实验，确认指标后再显式 promote 到生产模型目录
language: powershell
framework: lightgbm
tags: [lightgbm, training, experiments, promotion, recall-priority]
status: active
---

## 适用场景

需要调 LightGBM 参数、做论文对照实验，或准备替换 `backend/ml_models/` 中的生产风险模型时使用。目标是让实验可复现，并避免临时训练误覆盖生产模型。

## 做法

1. 参数文件放在 `backend/scripts/experiments/`。
2. 实验阶段统一加 `--run-name` 和 `--no-promote`。
3. 每个 run 保留自己的 `params.json`、`training_meta.json` 和 `model_report.md`。
4. 根据 `training_meta.json` 选出候选后，用同一参数文件重新运行 `--promote`。
5. 发布后核对 `backend/ml_models/model_config.json` 和 `docs/reports/model_report.md`。

## 示例

```powershell
cd backend

uv run python scripts/train_models.py `
  --params scripts/experiments/experiment.json `
  --run-name recall-min85 `
  --no-promote

uv run python scripts/train_models.py `
  --params scripts/experiments/experiment.json `
  --run-name final-recall-min85 `
  --promote

uv run pytest tests\training -q
```

发布后快速核对：

```powershell
cd backend
@'
import json
from pathlib import Path

config = json.loads(Path("ml_models/model_config.json").read_text(encoding="utf-8"))
meta = json.loads(Path("ml_models/training_meta.json").read_text(encoding="utf-8"))
metrics = meta["optimized_metrics"]

print(config["threshold_search_mode"], config["threshold_min_recall"])
print(metrics["recall"], metrics["f1"], metrics["auc"], metrics["brier_score"])
'@ | python -
```

## 为什么有效

`--no-promote` 把实验和生产模型目录分开，避免参数试错污染 `backend/ml_models/`。`--promote` 会先生成候选 run，再把候选产物发布到生产目录，同时保留上一版到 `backend/ml_models_previous/`。

## 何时不适用

- 只想导出默认参数时，用 `uv run python scripts/train_models.py --save-params <path>`。
- 只做一次临时本地烟测且不关心留档时，可以不命名 run，但这会走旧的默认生产写入行为，需要非常谨慎。

## 已知坑

- 对照实验不要混用 `f1` 和 `recall_priority` 阈值策略，否则指标变化很可能来自阈值目标，而不是训练参数。
- `backend/ml_runs/`、`backend/ml_models/`、`backend/ml_models_previous/` 是生成产物，不应提交。
- `compare.py` 主要支持两组详细对比；多组总览可直接读取多个 run 的 `training_meta.json` 汇总。

## 相关文档

- `docs/dev/lightgbm-training-experiments.md`
- `docs/training_guide.md`
- `backend/scripts/train_models.py`
- `backend/training/pipeline.py`
