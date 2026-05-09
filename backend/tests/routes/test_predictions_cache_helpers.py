from types import SimpleNamespace

from importlib.util import find_spec
import pytest

from prediction.domain.forecast_period_policy import UnsupportedForecastPeriodError
from prediction.schemas.commands import GetBPDataStatusQuery, PredictCommand
from services import prediction_run_metadata_service
from services.prediction_run_metadata_service import (
    MAX_PREDICTIONS_PER_USER,
    PredictionRecordRetentionService,
)


def test_old_prediction_run_metadata_service_is_removed():
    assert not hasattr(prediction_run_metadata_service, "PredictionRunMetadataService")


def test_old_prediction_cache_interfaces_are_removed():
    import prediction.domain as domain
    import prediction.domain.policies as policies

    assert find_spec("services.prediction_route_cache_service") is None
    assert find_spec("prediction.domain.cache_policy") is None
    assert "build_cache_snapshot" not in domain.__all__
    assert "build_cache_snapshot" not in policies.__all__
    assert not hasattr(domain, "build_cache_snapshot")
    assert not hasattr(policies, "build_cache_snapshot")


def test_command_objects_reject_unsupported_forecast_days():
    assert PredictCommand(user_id=1, forecast_days=None).forecast_days == 7
    assert PredictCommand(user_id=1, forecast_days=7).forecast_days == 7
    assert GetBPDataStatusQuery(user_id=1, forecast_days=None).forecast_days == 7
    assert GetBPDataStatusQuery(user_id=1, forecast_days="7").forecast_days == 7

    with pytest.raises(UnsupportedForecastPeriodError):
        PredictCommand(user_id=1, forecast_days=3)

    with pytest.raises(UnsupportedForecastPeriodError):
        GetBPDataStatusQuery(user_id=1, forecast_days=14)


class FakeSession:
    def __init__(self, get_result=None):
        self.get_result = get_result
        self.get_calls = []
        self.deleted = []

    def get(self, model, record_id):
        self.get_calls.append((model, record_id))
        return self.get_result

    def delete(self, record):
        self.deleted.append(record)


class FakeLimitField:
    def __init__(self, name):
        self.name = name

    def asc(self):
        return ("asc", self.name)


class FakeRecordLimitQuery:
    def __init__(self, count, oldest):
        self.count_value = count
        self.oldest = oldest
        self.filter_by_calls = []
        self.limit_value = None

    def filter_by(self, **kwargs):
        self.filter_by_calls.append(kwargs)
        return self

    def count(self):
        return self.count_value

    def order_by(self, *args):
        self.order_by_args = args
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def all(self):
        return self.oldest[: self.limit_value]


def test_enforce_prediction_limit_deletes_oldest_prediction_records(monkeypatch):
    oldest = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    record_query = FakeRecordLimitQuery(
        count=MAX_PREDICTIONS_PER_USER + 1,
        oldest=oldest,
    )
    fake_session = FakeSession()
    monkeypatch.setattr(
        prediction_run_metadata_service,
        "PredictionRecord",
        SimpleNamespace(
            query=record_query,
            created_at=FakeLimitField("created_at"),
        ),
    )
    monkeypatch.setattr(
        prediction_run_metadata_service.db, "session", fake_session, raising=False
    )

    PredictionRecordRetentionService().enforce_prediction_limit(user_id=42)

    assert record_query.filter_by_calls == [{"user_id": 42}, {"user_id": 42}]
    assert record_query.limit_value == 2
    assert fake_session.deleted == oldest
