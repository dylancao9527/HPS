from dataclasses import dataclass


@dataclass
class PredictionResult:
    prediction_id: int
    risk_probability: float
    risk_level: str
    risk_level_en: str
    risk_color: str
    bp_forecast: list
    forecast_days: int
    data_days_used: int
    total_history_days: int
    history_window_capped: bool
    data_range: str | None
    seasonality: dict
    training_meta: dict
    confidence_level: str | None
    confidence_reasons: list
    recommendations: list
    input_data: dict
    fusion_meta: dict
    created_at: str | None
    cache_mode: str
    prophet_prediction_id: int | None
