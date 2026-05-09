def build_confidence_reasons(
    training_meta_reasons=None,
    fusion_meta_reasons=None,
    model_strategy=None,
):
    rows = []
    for reason_type, reasons in (
        ("training_meta", training_meta_reasons),
        ("fusion_meta", fusion_meta_reasons),
    ):
        _ = reason_type
        for code in reasons or []:
            if not code:
                continue
            rows.append(code)
    if model_strategy:
        rows.append(model_strategy)
    return rows


def build_training_meta(training_meta):
    meta = training_meta or {}
    seasonality = meta.get("seasonality", {})
    return {
        **meta,
        "aggregation_mode": meta.get("aggregation_mode", "daily_mean"),
        "parameter_profile": meta.get("parameter_profile", "standard"),
        "seasonality": {
            "weekly_enabled": seasonality.get("weekly_enabled", False),
            "monthly_enabled": seasonality.get("monthly_enabled", False),
        },
        "avg_measurements_per_day": meta.get("avg_measurements_per_day"),
        "recent_sys_range_mean": meta.get("recent_sys_range_mean"),
        "recent_dia_range_mean": meta.get("recent_dia_range_mean"),
        "confidence_level": meta.get("confidence_level"),
        "confidence_reasons": list(meta.get("confidence_reasons") or []),
    }


def assemble_training_meta(prophet_record, item):
    if isinstance(getattr(item, "training_meta", None), dict):
        result = dict(item.training_meta)
        result.setdefault("confidence_reasons", [])
        if getattr(item, "cache_mode", None) == "model_reuse":
            result.setdefault("model_strategy", "reuse_existing_model")
        return result

    confidence_reasons = [
        reason.reason_code
        for reason in (item.confidence_reasons or [])
        if reason.reason_type == "training_meta"
    ]
    model_strategy = next(
        (
            reason.reason_code
            for reason in (item.confidence_reasons or [])
            if reason.reason_type == "model_strategy"
        ),
        None,
    )
    if not prophet_record or not prophet_record.training_meta_row:
        result = {"confidence_reasons": confidence_reasons}
        if model_strategy:
            result["model_strategy"] = model_strategy
        return result

    row = prophet_record.training_meta_row
    result = {
        "aggregation_mode": row.aggregation_mode,
        "parameter_profile": row.parameter_profile,
        "seasonality": {
            "weekly_enabled": row.weekly_enabled,
            "monthly_enabled": row.monthly_enabled,
        },
        "avg_measurements_per_day": row.avg_measurements_per_day,
        "recent_sys_range_mean": row.recent_sys_range_mean,
        "recent_dia_range_mean": row.recent_dia_range_mean,
        "confidence_level": row.confidence_level,
        "confidence_reasons": confidence_reasons,
    }
    if model_strategy:
        result["model_strategy"] = model_strategy
    return result
