def should_reuse_prophet_model(
    active_model,
    *,
    model_version,
    new_data_days_since_training,
    retrain_threshold_days,
):
    return bool(
        active_model
        and active_model.model_version == model_version
        and new_data_days_since_training < retrain_threshold_days
    )
