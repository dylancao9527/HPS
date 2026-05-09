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
from pathlib import Path

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

    print("高血压风险预测系统 — 模型训练")
    print()

    run_training(random_seed=random_seed, config=config)
    print("\n训练完成。")
    print(f"本次训练使用 seed: {random_seed}")


if __name__ == "__main__":
    main()
