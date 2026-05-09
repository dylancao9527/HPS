import numpy as np

from bp_series.domain import is_elevated_bp, is_high_bp


class TrendFusionConfig:
    """趋势融合可调参数。

    默认值与系统初始硬编码一致。通过构造函数注入可在不改动源码的前提下
    调整融合系数，便于实验和论文参数敏感性分析。
    """

    __slots__ = (
        "high_bp_weight",
        "elevated_bp_boost",
        "peak_bp_boost",
        "upward_trend_boost",
        "stable_low_discount",
        "meds_uncontrolled_boost",
        "peak_sys_threshold",
        "peak_dia_threshold",
        "upward_sys_slope",
        "upward_dia_slope",
        "stable_low_sys_ceiling",
        "stable_low_dia_ceiling",
        "clip_min",
        "clip_max",
    )

    def __init__(
        self,
        *,
        high_bp_weight: float = 0.08,
        elevated_bp_boost: float = 0.03,
        peak_bp_boost: float = 0.02,
        upward_trend_boost: float = 0.02,
        stable_low_discount: float = 0.02,
        meds_uncontrolled_boost: float = 0.02,
        peak_sys_threshold: float = 150.0,
        peak_dia_threshold: float = 95.0,
        upward_sys_slope: float = 5.0,
        upward_dia_slope: float = 3.0,
        stable_low_sys_ceiling: float = 120.0,
        stable_low_dia_ceiling: float = 80.0,
        clip_min: float = 0.01,
        clip_max: float = 0.99,
    ):
        self.high_bp_weight = high_bp_weight
        self.elevated_bp_boost = elevated_bp_boost
        self.peak_bp_boost = peak_bp_boost
        self.upward_trend_boost = upward_trend_boost
        self.stable_low_discount = stable_low_discount
        self.meds_uncontrolled_boost = meds_uncontrolled_boost
        self.peak_sys_threshold = peak_sys_threshold
        self.peak_dia_threshold = peak_dia_threshold
        self.upward_sys_slope = upward_sys_slope
        self.upward_dia_slope = upward_dia_slope
        self.stable_low_sys_ceiling = stable_low_sys_ceiling
        self.stable_low_dia_ceiling = stable_low_dia_ceiling
        self.clip_min = clip_min
        self.clip_max = clip_max


DEFAULT_TREND_FUSION_CONFIG = TrendFusionConfig()


def summarize_forecast_trend(bp_forecast):
    systolic = np.asarray([day["systolic"] for day in bp_forecast], dtype=float)
    diastolic = np.asarray([day["diastolic"] for day in bp_forecast], dtype=float)
    high_days = sum(
        1 for sys, dia in zip(systolic, diastolic) if is_high_bp(sys, dia)
    )
    elevated_days = sum(
        1 for sys, dia in zip(systolic, diastolic) if is_elevated_bp(sys, dia)
    )
    return {
        "forecast_days": len(bp_forecast),
        "avg_sys": round(float(np.mean(systolic)), 2),
        "avg_dia": round(float(np.mean(diastolic)), 2),
        "max_sys": round(float(np.max(systolic)), 2),
        "max_dia": round(float(np.max(diastolic)), 2),
        "sys_slope": round(float(systolic[-1] - systolic[0]), 2),
        "dia_slope": round(float(diastolic[-1] - diastolic[0]), 2),
        "sys_volatility": round(float(np.std(systolic)), 2),
        "dia_volatility": round(float(np.std(diastolic)), 2),
        "high_bp_days": high_days,
        "elevated_bp_days": elevated_days,
        "high_bp_ratio": round(high_days / max(len(bp_forecast), 1), 4),
        "elevated_bp_ratio": round(elevated_days / max(len(bp_forecast), 1), 4),
    }


def fuse_risk_with_trend(
    raw_probability, bp_forecast, *, bp_meds=None, config=None
):
    if config is None:
        config = DEFAULT_TREND_FUSION_CONFIG

    trend = summarize_forecast_trend(bp_forecast)
    trend_adjustment = 0.0
    trend_reasons = []
    medication_adjustment = 0.0
    medication_reasons = []

    if trend["high_bp_days"] > 0:
        delta = min(config.high_bp_weight, trend["high_bp_ratio"] * config.high_bp_weight)
        trend_adjustment += delta
        trend_reasons.append("high_bp_days")
    elif trend["elevated_bp_days"] >= max(1, trend["forecast_days"] // 2):
        trend_adjustment += config.elevated_bp_boost
        trend_reasons.append("elevated_bp_days")

    if trend["max_sys"] >= config.peak_sys_threshold or trend["max_dia"] >= config.peak_dia_threshold:
        trend_adjustment += config.peak_bp_boost
        trend_reasons.append("peak_bp")

    if trend["sys_slope"] >= config.upward_sys_slope or trend["dia_slope"] >= config.upward_dia_slope:
        trend_adjustment += config.upward_trend_boost
        trend_reasons.append("upward_trend")
    elif (
        trend["avg_sys"] < config.stable_low_sys_ceiling
        and trend["avg_dia"] < config.stable_low_dia_ceiling
        and trend["sys_slope"] <= 0
        and trend["high_bp_days"] == 0
    ):
        trend_adjustment -= config.stable_low_discount
        trend_reasons.append("stable_low_trend")

    if bp_meds == 1 and (
        trend["high_bp_days"] > 0
        or trend["max_sys"] >= config.peak_sys_threshold
        or trend["max_dia"] >= config.peak_dia_threshold
    ):
        medication_adjustment = config.meds_uncontrolled_boost
        medication_reasons.append("meds_uncontrolled_high_bp")

    adjustment = trend_adjustment + medication_adjustment
    reasons = trend_reasons + medication_reasons
    fused_probability = float(np.clip(
        raw_probability + adjustment, config.clip_min, config.clip_max
    ))
    return {
        "raw_probability": round(float(raw_probability), 4),
        "fused_probability": round(fused_probability, 4),
        "adjustment": round(adjustment, 4),
        "trend_adjustment": round(trend_adjustment, 4),
        "medication_adjustment": round(medication_adjustment, 4),
        "trend_summary": trend,
        "reasons": reasons,
    }
