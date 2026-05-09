"""Prediction service compatibility wrappers."""

from prediction.infrastructure import model_registry
from prediction.infrastructure import prophet_gateway
from prediction.infrastructure import risk_model_gateway


def __getattr__(name):
    if name == "AGGREGATION_MODE":
        return prophet_gateway.AGGREGATION_MODE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def predict_bp_trend_for_user(user_id, forecast_days=7):
    """Compatibility wrapper that delegates trend prediction to Prophet gateway."""
    return prophet_gateway.predict_bp_trend_for_user(user_id, forecast_days)


def predict_risk(user_data, bp_forecast, *, return_meta=False):
    """Compatibility wrapper that delegates risk scoring to risk model gateway."""
    probability, inference_meta = risk_model_gateway.score_risk_probability(
        user_data, bp_forecast
    )
    if return_meta:
        return probability, inference_meta
    return probability


def get_classification_threshold():
    """Return the saved LightGBM classification threshold."""
    config = model_registry.get_model_config()
    return float(config.get("classification_threshold", 0.5))
