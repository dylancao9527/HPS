import hashlib
import json

import numpy as np
import pandas as pd

from prediction.domain.bp_data_policy import MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION

AGGREGATION_MODE = "daily_mean"
MINIMUM_TRAIN_DAYS = MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION
SHORT_HISTORY_DAYS = 7
HIGH_CONFIDENCE_DAYS = 28
RECENT_VOLATILITY_WINDOW = 7
VOLATILE_SYS_DELTA = 10
VOLATILE_DIA_DELTA = 6
SPARSE_MEASUREMENTS_THRESHOLD = 1.5


from prediction.infrastructure.prophet_data_frame import (  # noqa: F401
    build_daily_training_frame,
    build_daily_training_frame_from_aggregates,
    build_daily_training_frame_from_series,
)


def build_training_context(
    daily,
    *,
    total_days,
    forecast_days,
    max_train_days,
    model_version="user-prophet-v1",
):
    latest_recorded_on = daily["date"].max().date()
    recent_slice = daily.tail(RECENT_VOLATILITY_WINDOW)
    avg_measurements_per_day = round(float(daily["measurements"].mean()), 2)
    recent_sys_range_mean = mean_abs_diff(recent_slice["systolic"])
    recent_dia_range_mean = mean_abs_diff(recent_slice["diastolic"])

    history_window_capped = bool(max_train_days and total_days > max_train_days)
    if history_window_capped:
        daily = daily.tail(max_train_days).reset_index(drop=True)

    data_days_used = len(daily)
    date_min = daily["date"].min().strftime("%Y-%m-%d")
    date_max = daily["date"].max().strftime("%Y-%m-%d")
    data_range = f"{date_min} ~ {date_max}"
    parameter_profile = select_parameter_profile(
        data_days_used,
        recent_sys_range_mean,
        recent_dia_range_mean,
    )
    confidence_level, confidence_reasons = build_confidence_meta(
        total_history_days=total_days,
        history_window_capped=history_window_capped,
        avg_measurements_per_day=avg_measurements_per_day,
        parameter_profile=parameter_profile,
    )
    data_signature = build_data_signature(
        daily,
        forecast_days,
        max_train_days=max_train_days,
        model_version=model_version,
    )

    return {
        "daily": daily,
        "data_days_used": data_days_used,
        "total_history_days": total_days,
        "data_range": data_range,
        "history_window_capped": history_window_capped,
        "parameter_profile": parameter_profile,
        "avg_measurements_per_day": avg_measurements_per_day,
        "recent_sys_range_mean": recent_sys_range_mean,
        "recent_dia_range_mean": recent_dia_range_mean,
        "confidence_level": confidence_level,
        "confidence_reasons": confidence_reasons,
        "data_signature": data_signature,
        "latest_recorded_on": latest_recorded_on,
    }


def count_new_data_days_since_training(daily: pd.DataFrame, trained_until) -> int:
    if trained_until is None or daily.empty:
        return 0
    dates = pd.to_datetime(daily["date"]).dt.date
    return int((dates > trained_until).sum())


def mean_abs_diff(values: pd.Series) -> float:
    numeric = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if len(numeric) < 2:
        return 0.0
    return round(float(np.abs(np.diff(numeric)).mean()), 2)


def select_parameter_profile(
    data_days_used: int,
    recent_sys_range_mean: float,
    recent_dia_range_mean: float,
) -> str:
    if data_days_used < SHORT_HISTORY_DAYS:
        return "short"

    if data_days_used >= HIGH_CONFIDENCE_DAYS and (
        recent_sys_range_mean >= VOLATILE_SYS_DELTA
        or recent_dia_range_mean >= VOLATILE_DIA_DELTA
    ):
        return "volatile"

    return "standard"


def build_confidence_meta(
    *,
    total_history_days: int,
    history_window_capped: bool,
    avg_measurements_per_day: float,
    parameter_profile: str,
) -> tuple[str, list[str]]:
    if total_history_days <= 6:
        level = "low"
    elif total_history_days < HIGH_CONFIDENCE_DAYS:
        level = "medium"
    else:
        level = "high"

    if history_window_capped and level == "high":
        level = "medium"

    reasons: list[str] = []
    if total_history_days <= 6:
        reasons.append("insufficient_days")
    if history_window_capped:
        reasons.append("window_capped")
    if avg_measurements_per_day < SPARSE_MEASUREMENTS_THRESHOLD:
        reasons.append("sparse_measurements")
    if parameter_profile == "volatile":
        reasons.append("high_volatility")

    return level, reasons


def build_data_signature(
    daily: pd.DataFrame,
    forecast_days: int,
    *,
    max_train_days,
    model_version,
) -> str:
    payload = {
        "forecast_days": forecast_days,
        "aggregation_mode": AGGREGATION_MODE,
        "prophet_max_train_days": max_train_days,
        "model_version": model_version,
        "daily": [
            {
                "date": row.date.strftime("%Y-%m-%d"),
                "systolic": round(float(row.systolic), 4),
                "diastolic": round(float(row.diastolic), 4),
                "measurements": int(row.measurements),
            }
            for row in daily.itertuples(index=False)
        ],
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
