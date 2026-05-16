"""
==============================================================================
模型训练脚本入口 (train_models.py)
==============================================================================
职责：
  - 作为统一训练入口保留原命令不变
  - 复用 backend/training/pipeline.py 中的训练编排
  - 保持测试中对 `_calculate_scale_pos_weight` 和 `find_best_threshold` 的导出兼容
==============================================================================
"""

from __future__ import annotations

import argparse
import secrets
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
import re

# Ensure backend root is on sys.path when run as `uv run python scripts/train_models.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training import _calculate_scale_pos_weight, find_best_threshold
from training.config import DEFAULT_CONFIG, SEED, TrainingConfig
from training.pipeline import (
    run_feature_ablation,
    run_multi_seed_audit,
    run_training,
    summarize_multi_seed_runs,
)


DEFAULT_RUNS_DIR = Path(__file__).resolve().parent.parent / "ml_runs"


def _slugify_run_name(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-._")
    return slug or "training"


def build_artifact_dir(run_name: str | None, output_root: str | Path) -> Path | None:
    if run_name is None:
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(output_root) / f"{timestamp}-{_slugify_run_name(run_name)}"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Train LightGBM model artifacts.")
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument(
        "--seed",
        type=int,
        default=None,
        help=f"Use a fixed random seed for reproducible training (default: {SEED}).",
    )
    seed_group.add_argument(
        "--random-seed",
        action="store_true",
        help="Use a fresh random seed for this training run.",
    )
    parser.add_argument(
        "--params",
        type=str,
        default=None,
        metavar="PATH",
        help="Load training config from a JSON file.",
    )
    parser.add_argument(
        "--save-params",
        type=str,
        default=None,
        metavar="PATH",
        help="Save current default training config to a JSON file and exit.",
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Save this training run into backend/ml_runs/<timestamp>-<run-name>.",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(DEFAULT_RUNS_DIR),
        metavar="PATH",
        help="Directory used for named training runs.",
    )
    promotion_group = parser.add_mutually_exclusive_group()
    promotion_group.add_argument(
        "--promote",
        action="store_true",
        help="Also update backend/ml_models and docs/reports with this run.",
    )
    promotion_group.add_argument(
        "--no-promote",
        action="store_true",
        help="Keep artifacts only in the run directory.",
    )
    return parser.parse_args(argv)


def resolve_random_seed(args, config: TrainingConfig | None = None) -> int:
    if getattr(args, "random_seed", False):
        return secrets.randbelow(2**31)
    if args.seed is not None:
        return args.seed
    if config is not None:
        return config.seed
    return SEED


def main(argv=None):
    args = parse_args(argv)

    if args.save_params:
        TrainingConfig().save(args.save_params)
        print(f"默认训练参数已保存至: {args.save_params}")
        return

    config = DEFAULT_CONFIG
    if args.params:
        config = TrainingConfig.load(args.params)
        print(f"从文件加载训练参数: {args.params}")
    random_seed = resolve_random_seed(args, config)
    effective_config = replace(config, seed=random_seed)
    artifact_dir = build_artifact_dir(args.run_name, args.output_root)
    promote = args.promote or (artifact_dir is None and not args.no_promote)
    if args.no_promote and artifact_dir is None:
        artifact_dir = build_artifact_dir("training", args.output_root)

    print("高血压风险预测系统 — 模型训练")
    print()

    if artifact_dir is not None:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        effective_config.save(artifact_dir / "params.json")
        print(f"本次训练产物目录: {artifact_dir}")
        if not promote:
            print("本次训练不会覆盖生产模型目录。")

    result = run_training(
        random_seed=random_seed,
        config=effective_config,
        artifact_dir=artifact_dir,
        promote=promote,
    )
    print("\n训练完成。")
    print(f"本次训练使用 seed: {random_seed}")
    if result and result.get("artifact_dir"):
        print(f"实验产物已保留: {result['artifact_dir']}")


if __name__ == "__main__":
    main()
