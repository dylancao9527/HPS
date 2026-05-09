from dataclasses import dataclass

from prediction.domain.forecast_period_policy import require_supported_forecast_days


@dataclass
class PredictCommand:
    user_id: int
    forecast_days: int | None = None
    use_trend_fusion: bool = True

    def __post_init__(self):
        self.forecast_days = require_supported_forecast_days(self.forecast_days)


@dataclass
class GetPredictionHistoryQuery:
    user_id: int
    page: int = 1
    per_page: int = 10
    start_date: str = ""
    end_date: str = ""


@dataclass
class DeletePredictionCommand:
    user_id: int
    prediction_id: int


@dataclass
class GetBPDataStatusQuery:
    user_id: int
    forecast_days: int | None = None

    def __post_init__(self):
        self.forecast_days = require_supported_forecast_days(self.forecast_days)
