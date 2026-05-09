import hashlib
import json


RISK_INPUT_KEY_FIELDS = (
    "age",
    "male",
    "BMI",
    "currentSmoker",
    "cigsPerDay",
    "BPMeds",
    "diabetes",
    "sysBP",
    "diaBP",
    "heartRate",
    "totChol",
    "glucose",
)


def build_prediction_run_key(
    *,
    user_id,
    forecast_days,
    model_version,
    data_signature,
    aggregation_mode,
    risk_inputs,
):
    payload = {
        "user_id": user_id,
        "forecast_days": forecast_days,
        "model_version": model_version or "unknown-model-version",
        "data_signature": data_signature or "unknown-data-signature",
        "aggregation_mode": aggregation_mode,
        "risk_inputs": {
            field: risk_inputs.get(field) for field in RISK_INPUT_KEY_FIELDS
        },
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
