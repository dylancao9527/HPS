from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "backend" / "ml_models"
DOCS_DIR = BASE_DIR / "docs" / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLD_SEARCH_MODES = {"recall_priority", "f1"}
MISSING_VALUE_STRATEGIES = {"native", "median_impute"}
BP_MEDS_POLICIES = {"neutralized_for_conservative_inference", "observed"}
LABEL_MODES = {"diagnosis_plus_rule", "diagnosis_only", "rule_only"}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_int(name: str, value: Any, *, minimum: int | None = None) -> None:
    if not _is_int(value):
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


def _require_ratio(name: str, value: Any) -> None:
    if not _is_number(value) or not 0 < float(value) < 1:
        raise ValueError(f"{name} must be between 0 and 1")


def _require_enum(name: str, value: Any, allowed: set[str]) -> None:
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {allowed_values}")


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

    def __post_init__(self) -> None:
        _require_int("seed", self.seed, minimum=0)
        _require_ratio("test_size", self.test_size)
        _require_ratio("threshold_valid_size", self.threshold_valid_size)
        _require_int("cv_splits", self.cv_splits, minimum=2)
        _require_int("early_stopping_rounds", self.early_stopping_rounds, minimum=1)
        _require_int("max_boost_rounds", self.max_boost_rounds, minimum=2)
        if self.early_stopping_rounds >= self.max_boost_rounds:
            raise ValueError("early_stopping_rounds must be < max_boost_rounds")
        _require_enum(
            "threshold_search_mode",
            self.threshold_search_mode,
            THRESHOLD_SEARCH_MODES,
        )
        if self.threshold_min_recall is not None:
            if (
                not _is_number(self.threshold_min_recall)
                or not 0 <= float(self.threshold_min_recall) <= 1
            ):
                raise ValueError("threshold_min_recall must be between 0 and 1")
        _require_enum(
            "missing_value_strategy",
            self.missing_value_strategy,
            MISSING_VALUE_STRATEGIES,
        )
        if not _is_number(self.learning_rate) or not 0 < float(self.learning_rate) <= 1:
            raise ValueError("learning_rate must be between 0 and 1")
        _require_enum("bp_meds_policy", self.bp_meds_policy, BP_MEDS_POLICIES)
        _require_enum("label_mode", self.label_mode, LABEL_MODES)
        if not isinstance(self.enable_feature_ablation, bool):
            raise ValueError("enable_feature_ablation must be a boolean")
        if not isinstance(self.multi_seed_audit_seeds, tuple):
            raise ValueError("multi_seed_audit_seeds must be a list of integers")
        for seed in self.multi_seed_audit_seeds:
            _require_int("multi_seed_audit_seeds item", seed, minimum=0)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["multi_seed_audit_seeds"] = list(self.multi_seed_audit_seeds)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrainingConfig":
        if not isinstance(data, dict):
            raise ValueError("Training config must be a JSON object")
        allowed_fields = {item.name for item in fields(cls)}
        unknown_fields = sorted(set(data) - allowed_fields)
        if unknown_fields:
            raise ValueError(f"Unknown training config fields: {unknown_fields}")
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
