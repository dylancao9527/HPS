from bp_series.domain import is_high_bp
from prediction.domain.bp_data_policy import MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION


MINIMUM_TRAIN_DAYS = MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION
KEY_PROFILE_FIELDS = (
    "age",
    "BMI",
    "currentSmoker",
    "BPMeds",
    "diabetes",
    "totChol",
    "glucose",
)


def _is_positive_binary(value):
    return value in (1, "1", True, "Yes", "yes")


def is_high_risk(risk_level):
    if not risk_level:
        return False
    normalized = str(risk_level).strip().lower()
    return normalized in {"高风险", "high"}


def is_low_risk(risk_level):
    if not risk_level:
        return False
    normalized = str(risk_level).strip().lower()
    return normalized in {"低风险", "low"}


def is_low_confidence(confidence_level):
    return str(confidence_level or "").strip().lower() == "low"


def has_recommendations(payload):
    return bool(payload.get("recommendations") or [])


def has_insufficient_data(payload):
    data_days_used = payload.get("data_days_used")
    if data_days_used is None:
        return False
    return data_days_used < MINIMUM_TRAIN_DAYS


def has_missing_key_profile_fields(payload):
    input_data = payload.get("input_data")
    if not input_data:
        return False
    if any(input_data.get(field) is None for field in KEY_PROFILE_FIELDS):
        return True
    return _is_positive_binary(input_data.get("currentSmoker")) and (
        input_data.get("cigsPerDay") is None
    )


def has_elevated_forecast(payload):
    for point in payload.get("bp_forecast") or []:
        if is_high_bp(point.get("systolic"), point.get("diastolic")):
            return True
    return False


def build_anomaly_flags(payload):
    flags = []
    high_risk = is_high_risk(payload.get("risk_level"))

    if high_risk and not has_recommendations(payload):
        flags.append("high_risk_without_recommendation")
    if high_risk and is_low_confidence(payload.get("confidence_level")):
        flags.append("high_risk_low_confidence")
    if has_insufficient_data(payload):
        flags.append("insufficient_data_prediction")
    if has_missing_key_profile_fields(payload):
        flags.append("missing_key_profile_fields")
    if is_low_risk(payload.get("risk_level")) and has_elevated_forecast(payload):
        flags.append("elevated_forecast_low_risk")

    return flags


def is_model_reused(payload):
    cache_mode = str(payload.get("cache_mode") or "").strip().lower()
    return cache_mode in {"model_reuse", "model_reused", "reuse_model", "reused_model"}


def build_governance_summary(records):
    rows = list(records or [])
    risk_distribution = {}
    confidence_distribution = {}
    anomaly_counts = {
        "high_risk_without_recommendation": 0,
        "high_risk_low_confidence": 0,
        "insufficient_data_prediction": 0,
        "missing_key_profile_fields": 0,
        "elevated_forecast_low_risk": 0,
    }
    high_risk_predictions = 0
    low_confidence_predictions = 0
    anomaly_predictions = 0
    insufficient_data_predictions = 0
    prophet_model_reuse_count = 0

    for row in rows:
        risk_key = row.get("risk_level") or "unknown"
        confidence_key = row.get("confidence_level") or "unknown"
        risk_distribution[risk_key] = risk_distribution.get(risk_key, 0) + 1
        confidence_distribution[confidence_key] = (
            confidence_distribution.get(confidence_key, 0) + 1
        )

        if is_high_risk(row.get("risk_level")):
            high_risk_predictions += 1
        if is_low_confidence(row.get("confidence_level")):
            low_confidence_predictions += 1
        if has_insufficient_data(row):
            insufficient_data_predictions += 1
        if is_model_reused(row):
            prophet_model_reuse_count += 1

        flags = row.get("anomaly_flags") or []
        if flags:
            anomaly_predictions += 1
        for flag in flags:
            anomaly_counts[flag] = anomaly_counts.get(flag, 0) + 1

    total_predictions = len(rows)
    return {
        "total_predictions": total_predictions,
        "risk_distribution": risk_distribution,
        "confidence_distribution": confidence_distribution,
        "anomaly_counts": anomaly_counts,
        "high_risk_predictions": high_risk_predictions,
        "low_confidence_predictions": low_confidence_predictions,
        "low_confidence_rate": round(
            low_confidence_predictions / total_predictions,
            4,
        )
        if total_predictions
        else 0,
        "anomaly_predictions": anomaly_predictions,
        "insufficient_data_predictions": insufficient_data_predictions,
        "prophet_model_reuse_count": prophet_model_reuse_count,
        "prophet_model_retrain_count": total_predictions - prophet_model_reuse_count,
    }
