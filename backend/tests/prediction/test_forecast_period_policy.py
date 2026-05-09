import pytest

from models.prediction import PredictionRecord
from models.user_prophet_model import UserProphetModel
from prediction.domain.forecast_period_policy import (
    DEFAULT_FORECAST_DAYS,
    FORECAST_PERIOD_ERROR_MESSAGE,
    UnsupportedForecastPeriodError,
    require_supported_forecast_days,
)


def test_forecast_period_policy_accepts_only_future_7_days():
    assert DEFAULT_FORECAST_DAYS == 7
    assert require_supported_forecast_days(None) == 7
    assert require_supported_forecast_days(7) == 7

    with pytest.raises(UnsupportedForecastPeriodError) as exc:
        require_supported_forecast_days(14)

    assert str(exc.value) == FORECAST_PERIOD_ERROR_MESSAGE


def test_forecast_period_storage_keeps_prediction_history_compact():
    prediction_columns = set(PredictionRecord.__table__.c.keys())
    model_constraints = {
        constraint.name for constraint in UserProphetModel.__table__.constraints
    }

    assert "forecast_days" not in prediction_columns
    assert "bp_forecast" in prediction_columns
    assert "ck_user_prophet_models_forecast_days_7" in model_constraints
