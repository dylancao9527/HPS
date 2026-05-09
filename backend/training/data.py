from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from .ml_schema import (
    BASE_TRAINING_DATASET,
    EXPORT_DATASET,
    LABEL_SOURCE_COLUMN,
    MODEL_CATEGORICAL_FEATURES,
    MODEL_FEATURE_COLUMNS,
    MODEL_TARGET_COLUMN,
)
from .config import (
    DATASETS_DIR,
    SEED,
    TRAINING_BP_MEDS_POLICY,
    TRAINING_LABEL_MODE,
)

RAW_FEATURE_COLUMNS = [
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
BASE_DATASET_LABEL_SOURCE = "base_dataset"
_HASH_COLUMNS = MODEL_FEATURE_COLUMNS + [LABEL_SOURCE_COLUMN, MODEL_TARGET_COLUMN]



def get_feature_sets():
    return [
        {"name": "full_contract", "columns": list(MODEL_FEATURE_COLUMNS)},
        {"name": "bp_only", "columns": ["sysBP", "diaBP"]},
        {"name": "bp_plus_core", "columns": ["age", "BMI", "sysBP", "diaBP"]},
        {
            "name": "drop_low_signal",
            "columns": [
                "male",
                "age",
                "totChol",
                "sysBP",
                "diaBP",
                "BMI",
                "heartRate",
                "glucose",
            ],
        },
    ]


def _read_training_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    raw_required = RAW_FEATURE_COLUMNS + [MODEL_TARGET_COLUMN]
    if not all(col in df.columns for col in raw_required):
        missing = [col for col in raw_required if col not in df.columns]
        raise ValueError(f"{path.name} 缺少必要列: {missing}")

    selected_columns = raw_required.copy()
    if LABEL_SOURCE_COLUMN in df.columns:
        selected_columns.append(LABEL_SOURCE_COLUMN)

    frame = df[selected_columns].copy()

    for col in MODEL_FEATURE_COLUMNS + [MODEL_TARGET_COLUMN]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")

    frame = frame.dropna(subset=[MODEL_TARGET_COLUMN]).reset_index(drop=True)
    if len(frame) == 0:
        raise ValueError(f"{path.name} 无有效样本，无法训练")

    if LABEL_SOURCE_COLUMN in frame.columns:
        frame[LABEL_SOURCE_COLUMN] = frame[LABEL_SOURCE_COLUMN].fillna(
            BASE_DATASET_LABEL_SOURCE
        )

    for col in MODEL_CATEGORICAL_FEATURES:
        frame[col] = frame[col].astype("Int64").astype("category")

    return frame


def _ensure_label_source(frame: pd.DataFrame, default_label_source: str) -> pd.DataFrame:
    enriched = frame.copy()
    if LABEL_SOURCE_COLUMN not in enriched.columns:
        enriched[LABEL_SOURCE_COLUMN] = default_label_source
    else:
        enriched[LABEL_SOURCE_COLUMN] = enriched[LABEL_SOURCE_COLUMN].fillna(
            default_label_source
        )
        enriched[LABEL_SOURCE_COLUMN] = enriched[LABEL_SOURCE_COLUMN].replace(
            "", default_label_source
        )
    enriched[LABEL_SOURCE_COLUMN] = enriched[LABEL_SOURCE_COLUMN].astype(str)
    return enriched


def _filter_export_data(export_data: pd.DataFrame, label_mode: str) -> pd.DataFrame:
    if label_mode == "diagnosis_plus_rule":
        return export_data
    if label_mode == "diagnosis_only":
        return export_data[
            export_data[LABEL_SOURCE_COLUMN] == "diagnosis"
        ].reset_index(drop=True)
    if label_mode == "rule_only":
        return export_data[export_data[LABEL_SOURCE_COLUMN] == "rule"].reset_index(
            drop=True
        )
    raise ValueError(f"不支持的 TRAINING_LABEL_MODE: {label_mode}")


def _apply_bp_meds_policy(merged: pd.DataFrame, bp_meds_policy: str) -> pd.DataFrame:
    adjusted = merged.copy()
    if bp_meds_policy == "neutralized_for_conservative_inference":
        adjusted["BPMeds"] = 0
    elif bp_meds_policy != "observed":
        raise ValueError(f"不支持的 TRAINING_BP_MEDS_POLICY: {bp_meds_policy}")

    adjusted["BPMeds"] = adjusted["BPMeds"].astype("Int64").astype("category")
    return adjusted


def _build_dataset_hash(merged: pd.DataFrame) -> str:
    hash_frame = merged[_HASH_COLUMNS].copy()
    for col in MODEL_CATEGORICAL_FEATURES:
        hash_frame[col] = hash_frame[col].astype("Int64")
    payload = json.dumps(
        hash_frame.to_dict(orient="records"),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _build_dataset_summary(
    base_data,
    export_data,
    merged,
    profile_name,
    feature_columns,
    random_seed,
    bp_meds_policy,
    label_mode,
):
    export_rows = len(export_data) if export_data is not None else 0
    export_pos_ratio = (
        round(float(export_data[MODEL_TARGET_COLUMN].mean()), 4)
        if export_data is not None and len(export_data) > 0
        else None
    )
    pos_count = int(merged[MODEL_TARGET_COLUMN].sum())
    total_count = int(len(merged))
    neg_count = total_count - pos_count
    pos_ratio = float(merged[MODEL_TARGET_COLUMN].mean())

    missing_summary = {
        col: int(merged[col].isna().sum())
        for col in feature_columns
        if int(merged[col].isna().sum()) > 0
    }
    label_source_summary = {
        str(label_source): int(count)
        for label_source, count in merged[LABEL_SOURCE_COLUMN].value_counts()
        .sort_index()
        .items()
    }

    return {
        "profile_name": profile_name,
        "random_seed": int(random_seed),
        "base_dataset_name": BASE_TRAINING_DATASET,
        "base_rows": int(len(base_data)),
        "base_pos_ratio": float(base_data[MODEL_TARGET_COLUMN].mean()),
        "export_rows": int(export_rows),
        "export_pos_ratio": export_pos_ratio,
        "total_rows": total_count,
        "positive_rows": pos_count,
        "negative_rows": neg_count,
        "positive_ratio": pos_ratio,
        "feature_columns": feature_columns,
        "missing_summary": missing_summary,
        "label_source_summary": label_source_summary,
        "bp_meds_policy": bp_meds_policy,
        "label_mode": label_mode,
        "dataset_hash": _build_dataset_hash(merged),
    }


def prepare_lgbm_data(
    random_seed: int = SEED,
    bp_meds_policy: str = TRAINING_BP_MEDS_POLICY,
    label_mode: str = TRAINING_LABEL_MODE,
):
    feature_columns = MODEL_FEATURE_COLUMNS
    categorical_features = MODEL_CATEGORICAL_FEATURES

    base_path = DATASETS_DIR / BASE_TRAINING_DATASET
    if not base_path.exists():
        raise FileNotFoundError(f"缺少基础训练文件: {base_path}")

    base_data = _ensure_label_source(
        _read_training_frame(base_path),
        BASE_DATASET_LABEL_SOURCE,
    )
    print("\n  [Profile] raw_baseline")
    print(f"  [数据源1] {BASE_TRAINING_DATASET}: {len(base_data)} 条")
    print(f"    正样本比例: {base_data[MODEL_TARGET_COLUMN].mean():.1%}")

    all_data = [base_data]
    export_data = None
    export_path = DATASETS_DIR / EXPORT_DATASET
    if export_path.exists():
        export_data = _ensure_label_source(
            _read_training_frame(export_path),
            BASE_DATASET_LABEL_SOURCE,
        )
        export_data = _filter_export_data(export_data, label_mode)
        if len(export_data) > 0:
            all_data.append(export_data)
            print(f"  [数据源2] {EXPORT_DATASET}: {len(export_data)} 条")
            print(f"    正样本比例: {export_data[MODEL_TARGET_COLUMN].mean():.1%}")
    else:
        print(f"  [数据源2] {EXPORT_DATASET} 不存在，仅使用基础数据集训练")

    merged = pd.concat(all_data, ignore_index=True).drop_duplicates()
    merged = _apply_bp_meds_policy(merged, bp_meds_policy)
    merged = merged.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    for col in categorical_features:
        merged[col] = merged[col].astype("Int64").astype("category")

    dataset_summary = _build_dataset_summary(
        base_data,
        export_data,
        merged,
        "raw_baseline",
        feature_columns,
        random_seed,
        bp_meds_policy,
        label_mode,
    )

    print(f"\n  合并后总样本: {len(merged)} 条")
    print(f"  合并后正样本比例: {merged[MODEL_TARGET_COLUMN].mean():.1%}")

    X = merged[feature_columns].copy()
    y = merged[MODEL_TARGET_COLUMN].astype(int)
    return X, y, feature_columns, categorical_features, dataset_summary
