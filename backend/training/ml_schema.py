from __future__ import annotations

import hashlib
import json
from typing import Any


BASE_TRAINING_DATASET = "framingham.csv"
EXPORT_DATASET = "training_data_export.csv"
MODEL_SCHEMA_VERSION = 2

MODEL_FEATURE_COLUMNS = [
    "male",
    "age",
    "currentSmoker",
    "cigsPerDay",
    "BPMeds",
    "diabetes",
    "totChol",
    "sysBP",
    "diaBP",
    "BMI",
    "heartRate",
    "glucose",
]
MODEL_TARGET_COLUMN = "Risk"
LABEL_SOURCE_COLUMN = "labelSource"
MODEL_CATEGORICAL_FEATURES = [
    "male",
    "currentSmoker",
    "BPMeds",
    "diabetes",
]
TRAINING_METADATA_COLUMNS = [LABEL_SOURCE_COLUMN]
TRAINING_EXPORT_COLUMNS = MODEL_FEATURE_COLUMNS + TRAINING_METADATA_COLUMNS + [MODEL_TARGET_COLUMN]


def build_feature_contract_hash(feature_columns: list[str], categorical_features: list[str]) -> str:
    payload = json.dumps(
        {
            "feature_columns": feature_columns,
            "categorical_features": categorical_features,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_binary_flag(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        if value in (0, 1):
            return int(value)
        raise ValueError("取值必须为 0 或 1")

    normalized = str(value).strip().lower()
    mapping = {
        "0": 0,
        "1": 1,
        "false": 0,
        "true": 1,
        "no": 0,
        "yes": 1,
    }
    if normalized in mapping:
        return mapping[normalized]
    raise ValueError("取值必须为 0/1 或等价布尔值")


def binary_flag_to_gender(value: int | None) -> str | None:
    if value is None:
        return None
    return "Male" if int(value) == 1 else "Female"


def binary_flag_to_yes_no(value: int | None) -> str | None:
    if value is None:
        return None
    return "Yes" if int(value) == 1 else "No"


def profile_to_model_feature_row(
    *,
    age: float | None,
    male: int | None,
    bmi: float | None,
    current_smoker: int | None,
    cigs_per_day: float | None,
    bp_meds: int | None,
    diabetes: int | None,
    tot_chol: float | None,
    sys_bp: float | None,
    dia_bp: float | None,
    heart_rate: float | None,
    glucose: float | None,
) -> dict[str, Any]:
    return {
        "male": male,
        "age": age,
        "currentSmoker": current_smoker,
        "cigsPerDay": cigs_per_day,
        "BPMeds": bp_meds,
        "diabetes": diabetes,
        "totChol": tot_chol,
        "sysBP": sys_bp,
        "diaBP": dia_bp,
        "BMI": bmi,
        "heartRate": heart_rate,
        "glucose": glucose,
    }
