from prediction.schemas.results import PredictionResult


def build_prediction_run_mode(prophet_result, training_meta):
    model_strategy = prophet_result.get("model_strategy") or training_meta.get(
        "model_strategy"
    )
    return "model_reuse" if model_strategy == "reuse_existing_model" else "fresh_train"


def build_save_payload(
    *,
    command,
    prophet_result,
    training_meta,
    input_data,
    fusion_meta,
    risk_probability,
    risk_level,
    recommendations,
    prediction_run_key,
):
    return {
        "user_id": command.user_id,
        "forecast_days": command.forecast_days,
        "bp_forecast": prophet_result["forecast"],
        "data_days_used": prophet_result["data_days_used"],
        "total_history_days": prophet_result["total_history_days"],
        "history_window_capped": prophet_result["history_window_capped"],
        "data_range": prophet_result["data_range"],
        "cache_key": prediction_run_key,
        "training_meta": training_meta,
        "input_data": input_data,
        "fusion_meta": fusion_meta,
        "risk_probability": round(risk_probability, 4),
        "risk_level": risk_level,
        "recommendations": recommendations,
    }


def build_prediction_result(
    *,
    saved_prediction,
    risk_probability,
    risk_level,
    risk_level_en,
    risk_color,
    prophet_result,
    command,
    training_meta,
    recommendations,
    input_data,
    fusion_meta,
    prediction_run_mode,
):
    if isinstance(saved_prediction, tuple):
        record, prophet_record = saved_prediction
        created_at = record.created_at.isoformat() if record.created_at else None
        prediction_id = record.id
        prophet_prediction_id = prophet_record.id if prophet_record else None
    else:
        created_at = None
        prediction_id = 0
        prophet_prediction_id = None

    return PredictionResult(
        prediction_id=prediction_id,
        risk_probability=round(risk_probability, 4),
        risk_level=risk_level,
        risk_level_en=risk_level_en,
        risk_color=risk_color,
        bp_forecast=prophet_result["forecast"],
        forecast_days=command.forecast_days,
        data_days_used=prophet_result["data_days_used"],
        total_history_days=prophet_result["total_history_days"],
        history_window_capped=prophet_result["history_window_capped"],
        data_range=prophet_result["data_range"],
        seasonality=prophet_result.get("seasonality", {}),
        training_meta=training_meta,
        confidence_level=training_meta.get("confidence_level"),
        confidence_reasons=training_meta.get("confidence_reasons", []),
        recommendations=recommendations,
        input_data=input_data,
        fusion_meta=fusion_meta,
        created_at=created_at,
        cache_mode=prediction_run_mode,
        prophet_prediction_id=prophet_prediction_id,
    )
