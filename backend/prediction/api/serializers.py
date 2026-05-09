from dataclasses import asdict, is_dataclass



def serialize_prediction_result(result):
    if is_dataclass(result):
        payload = asdict(result)
    else:
        payload = dict(result)

    training_meta = payload.get("training_meta") or {}
    if not isinstance(training_meta, dict):
        training_meta = {}

    seasonality = training_meta.get("seasonality")
    if seasonality is None:
        seasonality = payload.get("seasonality") or {}

    confidence_level = training_meta.get("confidence_level")
    if confidence_level is None:
        confidence_level = payload.get("confidence_level")

    confidence_reasons = training_meta.get("confidence_reasons")
    if confidence_reasons is None:
        confidence_reasons = payload.get("confidence_reasons") or []

    payload["training_meta"] = {
        **training_meta,
        "seasonality": seasonality,
        "confidence_level": confidence_level,
        "confidence_reasons": confidence_reasons,
    }
    payload["seasonality"] = seasonality
    payload["confidence_level"] = confidence_level
    payload["confidence_reasons"] = confidence_reasons
    payload["id"] = payload["prediction_id"]
    payload["threshold_positive"] = payload.get("threshold_positive")
    payload["classification_threshold"] = payload.get("classification_threshold")
    return payload
