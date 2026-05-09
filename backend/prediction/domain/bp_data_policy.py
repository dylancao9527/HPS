MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION = 3
RECOMMENDED_HISTORY_DAYS_PER_FORECAST_DAY_MIN = 3
RECOMMENDED_HISTORY_DAYS_PER_FORECAST_DAY_MAX = 5
RECOMMENDED_BP_RECORDS_PER_HISTORY_DAY = 3


class InsufficientBPDataForPredictionError(ValueError):
    """Raised when BP records do not satisfy the prediction minimum."""


def build_bp_data_status(*, total_records, total_days, forecast_days):
    recommended_days_min = (
        forecast_days * RECOMMENDED_HISTORY_DAYS_PER_FORECAST_DAY_MIN
    )
    recommended_days_max = (
        forecast_days * RECOMMENDED_HISTORY_DAYS_PER_FORECAST_DAY_MAX
    )
    minimum_days = MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION

    if not total_records:
        status = "no_data"
    elif total_days < minimum_days:
        status = "insufficient"
    elif total_days < recommended_days_min:
        status = "warning"
    else:
        status = "recommended"

    return {
        "total_records": total_records,
        "total_days": total_days,
        "forecast_days": forecast_days,
        "minimum_days": minimum_days,
        "recommended_days_min": recommended_days_min,
        "recommended_days_max": recommended_days_max,
        "recommended_records_min": (
            recommended_days_min * RECOMMENDED_BP_RECORDS_PER_HISTORY_DAY
        ),
        "recommended_records_max": (
            recommended_days_max * RECOMMENDED_BP_RECORDS_PER_HISTORY_DAY
        ),
        "meets_minimum": total_days >= minimum_days,
        "meets_recommended": total_days >= recommended_days_min,
        "status": status,
    }


def require_minimum_bp_days_for_prediction(bp_data_status):
    if bp_data_status.get("meets_minimum"):
        return

    minimum_days = int(
        bp_data_status.get("minimum_days")
        or MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION
    )
    raise InsufficientBPDataForPredictionError(
        f"血压记录不足：请至少记录 {minimum_days} 个自然日后再进行预测"
    )
