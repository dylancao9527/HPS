from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "backend" / "ml_models"
DOCS_DIR = BASE_DIR / "docs" / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class TrainingConfig:
    seed: int = 42
    test_size: float = 0.2
    threshold_valid_size: float = 0.1
    cv_splits: int = 5
    early_stopping_rounds: int = 50
    max_boost_rounds: int = 1000
    threshold_search_mode: str = "recall_priority"
    threshold_min_recall: float = 0.75
    missing_value_strategy: str = "native"
    learning_rate: float = 0.05
    bp_meds_policy: str = "neutralized_for_conservative_inference"
    label_mode: str = "diagnosis_plus_rule"
    enable_feature_ablation: bool = False
    multi_seed_audit_seeds: tuple = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["multi_seed_audit_seeds"] = list(self.multi_seed_audit_seeds)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrainingConfig":
        seeds = tuple(data.get("multi_seed_audit_seeds", ()) or ())
        return cls(
            seed=data.get("seed", 42),
            test_size=data.get("test_size", 0.2),
            threshold_valid_size=data.get("threshold_valid_size", 0.1),
            cv_splits=data.get("cv_splits", 5),
            early_stopping_rounds=data.get("early_stopping_rounds", 50),
            max_boost_rounds=data.get("max_boost_rounds", 1000),
            threshold_search_mode=data.get("threshold_search_mode", "recall_priority"),
            threshold_min_recall=data.get("threshold_min_recall", 0.75),
            missing_value_strategy=data.get("missing_value_strategy", "native"),
            learning_rate=data.get("learning_rate", 0.05),
            bp_meds_policy=data.get("bp_meds_policy", "neutralized_for_conservative_inference"),
            label_mode=data.get("label_mode", "diagnosis_plus_rule"),
            enable_feature_ablation=data.get("enable_feature_ablation", False),
            multi_seed_audit_seeds=seeds,
        )

    def save(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "TrainingConfig":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


DEFAULT_CONFIG = TrainingConfig()

# Backward-compatible module-level constants
SEED = DEFAULT_CONFIG.seed
TEST_SIZE = DEFAULT_CONFIG.test_size
THRESHOLD_VALID_SIZE = DEFAULT_CONFIG.threshold_valid_size
CV_SPLITS = DEFAULT_CONFIG.cv_splits
EARLY_STOPPING_ROUNDS = DEFAULT_CONFIG.early_stopping_rounds
MAX_BOOST_ROUNDS = DEFAULT_CONFIG.max_boost_rounds
THRESHOLD_SEARCH_MODE = DEFAULT_CONFIG.threshold_search_mode
THRESHOLD_MIN_RECALL = DEFAULT_CONFIG.threshold_min_recall
TRAINING_MISSING_VALUE_STRATEGY = DEFAULT_CONFIG.missing_value_strategy
ENABLE_FEATURE_ABLATION_EXPERIMENTS = DEFAULT_CONFIG.enable_feature_ablation
MULTI_SEED_AUDIT_SEEDS = []
TRAINING_BP_MEDS_POLICY = DEFAULT_CONFIG.bp_meds_policy
TRAINING_LABEL_MODE = DEFAULT_CONFIG.label_mode
