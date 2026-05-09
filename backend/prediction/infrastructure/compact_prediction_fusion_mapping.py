from prediction.domain.trend_policy import summarize_forecast_trend
from prediction.infrastructure.compact_prediction_forecast_mapping import (
    assemble_forecast,
)


def build_fusion_meta(fusion_meta):
    return {
        "raw_probability": fusion_meta.get("raw_probability", 0.0),
        "fused_probability": fusion_meta.get("fused_probability", 0.0),
        "bp_meds_input": fusion_meta.get("bp_meds_input", 0),
        "bp_meds_model_value": fusion_meta.get("bp_meds_model_value", 0),
        "bp_meds_policy": fusion_meta.get(
            "bp_meds_policy", "neutralized_for_conservative_inference"
        ),
        "medication_adjustment": fusion_meta.get("medication_adjustment", 0.0),
        "trend_adjustment": fusion_meta.get("trend_adjustment", 0.0),
        "adjustment": fusion_meta.get("adjustment", 0.0),
        "reasons": list(fusion_meta.get("reasons") or []),
    }


def assemble_fusion_meta(item, prophet_record=None):
    if isinstance(getattr(item, "fusion_meta", None), dict):
        result = dict(item.fusion_meta)
        forecast = assemble_forecast(prophet_record, item)
        if forecast and "trend_summary" not in result:
            result["trend_summary"] = summarize_forecast_trend(forecast)
        result.setdefault("reasons", [])
        return result

    compact_fusion_reasons = [
        reason.reason_code
        for reason in (item.confidence_reasons or [])
        if reason.reason_type == "fusion_meta"
    ]
    if not item.fusion_meta:
        return {"reasons": compact_fusion_reasons}

    forecast = assemble_forecast(prophet_record, item)
    trend_summary = summarize_forecast_trend(forecast) if forecast else None
    raw_probability = item.fusion_meta.raw_probability
    fused_probability = item.fusion_meta.fused_probability
    medication_adjustment = item.fusion_meta.medication_adjustment
    adjustment = round(fused_probability - raw_probability, 4)
    trend_adjustment = round(adjustment - medication_adjustment, 4)
    return {
        "raw_probability": raw_probability,
        "fused_probability": fused_probability,
        "bp_meds_input": item.fusion_meta.bp_meds_input,
        "bp_meds_model_value": item.fusion_meta.bp_meds_model_value,
        "bp_meds_policy": item.fusion_meta.bp_meds_policy,
        "medication_adjustment": medication_adjustment,
        "trend_adjustment": trend_adjustment,
        "adjustment": adjustment,
        "trend_summary": trend_summary,
        "reasons": compact_fusion_reasons,
    }
