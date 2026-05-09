import numpy as np
import pandas as pd

from training.ml_schema import (
    MODEL_CATEGORICAL_FEATURES,
    MODEL_FEATURE_COLUMNS,
    profile_to_model_feature_row,
)
from prediction.domain.risk_policy import resolve_inference_bp_meds
from prediction.infrastructure import model_registry



def _build_feature_frame(user_data, bp_forecast, model_config):
    avg_sys = np.mean([day["systolic"] for day in bp_forecast])
    avg_dia = np.mean([day["diastolic"] for day in bp_forecast])
    feature_columns = model_config.get("feature_columns", MODEL_FEATURE_COLUMNS)
    categorical_features = model_config.get(
        "categorical_features", MODEL_CATEGORICAL_FEATURES
    )
    resolved_bp_meds, inference_meta = resolve_inference_bp_meds(
        user_data.get("BPMeds")
    )
    features = pd.DataFrame(
        [
            profile_to_model_feature_row(
                age=user_data.get("age"),
                male=user_data.get("male"),
                bmi=user_data.get("BMI", user_data.get("bmi")),
                current_smoker=user_data.get("currentSmoker"),
                cigs_per_day=user_data.get("cigsPerDay"),
                bp_meds=resolved_bp_meds,
                diabetes=user_data.get("diabetes"),
                tot_chol=user_data.get("totChol"),
                sys_bp=avg_sys,
                dia_bp=avg_dia,
                heart_rate=user_data.get("heartRate", user_data.get("heart_rate")),
                glucose=user_data.get("glucose"),
            )
        ]
    )
    features = features.reindex(columns=feature_columns)
    for col in feature_columns:
        if col in categorical_features:
            features[col] = pd.to_numeric(features[col], errors="coerce")
        else:
            features[col] = pd.to_numeric(features[col], errors="coerce").astype(float)
    for col in categorical_features:
        if col in features:
            features[col] = pd.Categorical(features[col], categories=[0, 1])

    return features, inference_meta


def score_risk_probability(user_data, bp_forecast):
    model_config = model_registry.get_model_config()
    features, inference_meta = _build_feature_frame(
        user_data,
        bp_forecast,
        model_config,
    )
    predictions = np.asarray(
        model_registry.get_lgbm_model().predict(features), dtype=float
    ).reshape(-1)
    return float(predictions[0]), inference_meta
