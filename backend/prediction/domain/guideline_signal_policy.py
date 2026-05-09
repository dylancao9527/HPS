def build_guideline_signal(
    *,
    risk_level_en,
    fusion_meta,
    training_meta,
    data_days_used,
):
    trend_summary = (fusion_meta or {}).get("trend_summary", {})
    avg_sys = trend_summary.get("avg_sys", 120)
    avg_dia = trend_summary.get("avg_dia", 80)
    return {
        "risk_level": risk_level_en,
        "high_bp_days": trend_summary.get("high_bp_days", 0),
        "trend_direction": derive_guideline_trend_direction(
            fusion_meta=fusion_meta,
        ),
        "record_days": data_days_used,
        "confidence_level": (training_meta or {}).get("confidence_level"),
        "bp_grade": derive_bp_grade(avg_sys, avg_dia),
    }


def derive_guideline_trend_direction(*, fusion_meta):
    trend_summary = (fusion_meta or {}).get("trend_summary", {})
    reasons = set((fusion_meta or {}).get("reasons", []))

    sys_volatility = trend_summary.get("sys_volatility")
    dia_volatility = trend_summary.get("dia_volatility")
    if (
        sys_volatility is not None
        and sys_volatility >= 6
        or dia_volatility is not None
        and dia_volatility >= 4
    ):
        return "volatile"

    if "upward_trend" in reasons:
        return "upward"

    sys_slope = trend_summary.get("sys_slope")
    dia_slope = trend_summary.get("dia_slope")
    if (
        sys_slope is not None
        and sys_slope >= 5
        or dia_slope is not None
        and dia_slope >= 3
    ):
        return "upward"

    return "stable"


def derive_bp_grade(avg_sys, avg_dia):
    if avg_sys >= 180 or avg_dia >= 110:
        return "grade3"
    if avg_sys >= 160 or avg_dia >= 100:
        return "grade2"
    if avg_sys >= 140 or avg_dia >= 90:
        return "grade1"
    if avg_sys >= 120 or avg_dia >= 80:
        return "normal_high"
    return "normal"
