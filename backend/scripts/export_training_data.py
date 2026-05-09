from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

# Ensure backend root is on sys.path when run as `uv run python scripts/export_training_data.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from training.ml_schema import EXPORT_DATASET
from training.config import DATASETS_DIR


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Export local LightGBM training CSV from the application database."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATASETS_DIR / EXPORT_DATASET,
        help="CSV output path.",
    )
    parser.add_argument(
        "--recent-bp-count",
        type=int,
        default=None,
        help="Number of recent blood pressure records to average per user.",
    )
    return parser.parse_args(argv)


def run_local_training_export(
    *,
    output_path: Path,
    recent_bp_count: int | None = None,
    app_factory: Callable | None = None,
    exporter: Callable[[], str] | None = None,
) -> Path:
    if app_factory is None:
        from app import create_app as app_factory

    if exporter is None:
        from services.export_service import export_training_csv as exporter

    config_override = {"INIT_ADMIN_ON_STARTUP": False}
    if recent_bp_count is not None:
        config_override["EXPORT_RECENT_BP_COUNT"] = recent_bp_count

    app = app_factory(config_override)
    with app.app_context():
        csv_text = exporter()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(csv_text, encoding="utf-8")
    return output_path.resolve()


def main(argv=None):
    args = parse_args(argv)
    exported_path = run_local_training_export(
        output_path=args.output,
        recent_bp_count=args.recent_bp_count,
    )
    print(f"Training CSV exported: {exported_path}")
    print("Next: uv run python scripts/train_models.py")


if __name__ == "__main__":
    main()
