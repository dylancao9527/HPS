from prediction.schemas.input_snapshot import (
    LEGACY_CACHE_SNAPSHOT_KEY,
    LEGACY_PROPHET_CACHE_KEY,
    MODEL_STATE_SNAPSHOT_KEY,
    PREDICTION_RUN_KEY,
)


def build_input_snapshot(input_data):
    snapshot = {
        "age": input_data["age"],
        "male": input_data["male"],
        "currentSmoker": input_data["currentSmoker"],
        "cigsPerDay": input_data.get("cigsPerDay"),
        "BPMeds": input_data["BPMeds"],
        "diabetes": input_data["diabetes"],
        "totChol": input_data.get("totChol"),
        "sysBP": input_data["sysBP"],
        "diaBP": input_data["diaBP"],
        "BMI": input_data["BMI"],
        "heartRate": input_data.get("heartRate"),
        "glucose": input_data.get("glucose"),
        "_tot_chol_filled": input_data.get("_tot_chol_filled"),
        "_glucose_filled": input_data.get("_glucose_filled"),
    }
    for key in (
        MODEL_STATE_SNAPSHOT_KEY,
        PREDICTION_RUN_KEY,
        LEGACY_CACHE_SNAPSHOT_KEY,
        LEGACY_PROPHET_CACHE_KEY,
    ):
        if key in input_data:
            snapshot[key] = input_data.get(key)
    return snapshot


def assemble_input_data(item, prophet_record=None):
    snapshot = item.input_snapshot
    if not snapshot:
        return {}
    if isinstance(snapshot, dict):
        payload = dict(snapshot)
        if (
            MODEL_STATE_SNAPSHOT_KEY not in payload
            and LEGACY_CACHE_SNAPSHOT_KEY in payload
        ):
            payload[MODEL_STATE_SNAPSHOT_KEY] = payload.get(LEGACY_CACHE_SNAPSHOT_KEY)
        if PREDICTION_RUN_KEY not in payload:
            if LEGACY_PROPHET_CACHE_KEY in payload:
                payload[PREDICTION_RUN_KEY] = payload.get(LEGACY_PROPHET_CACHE_KEY)
            elif prophet_record and getattr(prophet_record, "cache_key", None):
                payload[PREDICTION_RUN_KEY] = prophet_record.cache_key
        return payload
    payload = {
        "age": snapshot.age,
        "male": snapshot.male,
        "currentSmoker": snapshot.current_smoker,
        "cigsPerDay": snapshot.cigs_per_day,
        "BPMeds": snapshot.bp_meds,
        "diabetes": snapshot.diabetes,
        "totChol": snapshot.tot_chol,
        "sysBP": snapshot.sys_bp,
        "diaBP": snapshot.dia_bp,
        "BMI": snapshot.bmi,
        "heartRate": snapshot.heart_rate,
        "glucose": snapshot.glucose,
        "_tot_chol_filled": snapshot.tot_chol is not None,
        "_glucose_filled": snapshot.glucose is not None,
        MODEL_STATE_SNAPSHOT_KEY: None,
    }
    if prophet_record:
        payload[PREDICTION_RUN_KEY] = prophet_record.cache_key
    return payload
