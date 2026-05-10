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
    model_columns = set(UserProphetModel.__table__.c.keys())
    model_constraints = {
        constraint.name for constraint in UserProphetModel.__table__.constraints
    }
    model_indexes = {
        index.name: [column.name for column in index.columns]
        for index in UserProphetModel.__table__.indexes
    }
    removed_model_columns = {
        "forecast_days",
        "aggregation_mode",
        "data_days_used",
        "total_history_days",
        "history_window_capped",
        "parameter_profile",
        "weekly_enabled",
        "monthly_enabled",
    }

    assert "forecast_days" not in prediction_columns
    assert removed_model_columns.isdisjoint(model_columns)
    assert "bp_forecast" in prediction_columns
    assert "ck_user_prophet_models_forecast_days_7" not in model_constraints
    assert set(model_indexes) == {
        "ix_user_prophet_models_active_slot_trained",
        "ix_user_prophet_models_user_id",
    }
    assert model_indexes["ix_user_prophet_models_active_slot_trained"] == [
        "user_id",
        "is_active",
        "trained_at",
        "id",
    ]
    assert model_indexes["ix_user_prophet_models_user_id"] == ["user_id"]
