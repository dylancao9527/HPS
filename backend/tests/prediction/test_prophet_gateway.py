import inspect
from datetime import date
from types import SimpleNamespace

import pandas as pd
from flask import Flask

from bp_series.domain import DailyBPSeriesPoint
from prediction.infrastructure import prophet_gateway
from prediction.infrastructure.prophet_model_lifecycle import ProphetModelLifecycle
from prediction.infrastructure.prophet_model_store import LocalProphetModelStore
from prediction.infrastructure.prophet_lifecycle_policy import should_reuse_prophet_model
from prediction.infrastructure.prophet_training_context import (
    build_daily_training_frame,
    build_training_context,
)


class FakeProphetModel:
    def __init__(self, name):
        self.name = name
        self.fit_calls = []

    def fit(self, frame):
        self.fit_calls.append(frame.copy())
        return self


class FakeModelCache:
    def __init__(self):
        self.set_calls = []

    def set(self, cache_key, payload):
        self.set_calls.append((cache_key, payload))


def test_prophet_model_store_uses_fixed_7_day_free_storage_keys(tmp_path):
    store = LocalProphetModelStore(tmp_path)

    storage_key = store.build_storage_key(
        user_id=42,
        model_version="user-prophet-v1",
        data_signature="current-signature",
    )

    assert storage_key == "user_42/user-prophet-v1/current-signature"

    legacy_dir = tmp_path / "user_42" / "fd_7" / "user-prophet-v1" / "legacy-signature"
    legacy_dir.mkdir(parents=True)
    current_dir = tmp_path / "user_42" / "user-prophet-v1" / "current-signature"
    current_dir.mkdir(parents=True)

    assert store.list_storage_keys() == [
        "user_42/fd_7/user-prophet-v1/legacy-signature",
        "user_42/user-prophet-v1/current-signature",
    ]


def test_training_context_builder_aggregates_daily_sequence_and_confidence():
    records = [
        SimpleNamespace(
            recorded_at=pd.Timestamp("2026-04-20 08:00"),
            systolic_bp=130,
            diastolic_bp=82,
        ),
        SimpleNamespace(
            recorded_at=pd.Timestamp("2026-04-20 20:00"),
            systolic_bp=134,
            diastolic_bp=86,
        ),
        SimpleNamespace(
            recorded_at=pd.Timestamp("2026-04-21 08:00"),
            systolic_bp=140,
            diastolic_bp=90,
        ),
        SimpleNamespace(
            recorded_at=pd.Timestamp("2026-04-22 08:00"),
            systolic_bp=142,
            diastolic_bp=91,
        ),
    ]

    daily = build_daily_training_frame(records)
    context = build_training_context(
        daily,
        total_days=len(daily),
        forecast_days=7,
        max_train_days=90,
    )

    assert daily["systolic"].tolist() == [132.0, 140.0, 142.0]
    assert daily["measurements"].tolist() == [2, 1, 1]
    assert context["data_days_used"] == 3
    assert context["data_range"] == "2026-04-20 ~ 2026-04-22"
    assert context["parameter_profile"] == "short"
    assert context["confidence_level"] == "low"
    assert context["confidence_reasons"] == [
        "insufficient_days",
        "sparse_measurements",
    ]
    assert len(context["data_signature"]) == 64


class FakeDailyBPSeriesRepository:
    def __init__(self):
        self.calls = []

    def count_daily_series_days(self, *, user_id):
        self.calls.append({"method": "count_daily_series_days", "user_id": user_id})
        return 5

    def load_recent_daily_series(self, *, user_id, limit, ascending):
        self.calls.append(
            {
                "method": "load_recent_daily_series",
                "user_id": user_id,
                "limit": limit,
                "ascending": ascending,
            }
        )
        return [
            DailyBPSeriesPoint(date(2026, 4, 20), 132.0, 84.0, 2),
            DailyBPSeriesPoint(date(2026, 4, 21), 140.0, 90.0, 1),
            DailyBPSeriesPoint(date(2026, 4, 22), 142.0, 91.0, 1),
        ]


def test_load_daily_records_uses_daily_bp_series_training_window(monkeypatch):
    repository = FakeDailyBPSeriesRepository()
    monkeypatch.setattr(
        prophet_gateway,
        "DailyBPSeriesRepository",
        lambda: repository,
    )

    daily, total_days = prophet_gateway._load_daily_records(42, max_train_days=3)

    assert total_days == 5
    assert daily["systolic"].tolist() == [132.0, 140.0, 142.0]
    assert daily["diastolic"].tolist() == [84.0, 90.0, 91.0]
    assert daily["measurements"].tolist() == [2, 1, 1]
    assert repository.calls == [
        {"method": "count_daily_series_days", "user_id": 42},
        {
            "method": "load_recent_daily_series",
            "user_id": 42,
            "limit": 3,
            "ascending": True,
        },
    ]


def test_inspect_prophet_state_counts_new_days_outside_training_window(monkeypatch):
    app = Flask(__name__)
    app.config.update(
        PROPHET_MAX_TRAIN_DAYS=3,
        PROPHET_RETRAIN_AFTER_DAYS=3,
    )
    daily_repository = FakeDailyBPSeriesRepository()
    prediction_repository = SimpleNamespace(
        get_active_prophet_model=lambda user_id, forecast_days: SimpleNamespace(
            model_version=prophet_gateway.PROPHET_MODEL_VERSION,
            data_signature="active-signature",
            trained_until=date(2026, 4, 20),
            storage_key=None,
        )
    )

    def count_new_days(*, user_id, after_date):
        daily_repository.calls.append(
            {
                "method": "count_daily_series_days_after",
                "user_id": user_id,
                "after_date": after_date,
            }
        )
        return 2

    daily_repository.count_daily_series_days_after = count_new_days
    monkeypatch.setattr(
        prophet_gateway,
        "DailyBPSeriesRepository",
        lambda: daily_repository,
    )

    with app.app_context():
        model_state = prophet_gateway.inspect_prophet_model_state_for_user(
            42,
            forecast_days=7,
            repository=prediction_repository,
        )

    assert model_state["context"]["total_history_days"] == 5
    assert model_state["context"]["data_days_used"] == 3
    assert model_state["context"]["history_window_capped"] is True
    assert model_state["new_data_days_since_training"] == 2
    assert model_state["reuse_existing_model"] is True
    assert model_state["data_signature"] == "active-signature"
    assert daily_repository.calls == [
        {"method": "count_daily_series_days", "user_id": 42},
        {
            "method": "load_recent_daily_series",
            "user_id": 42,
            "limit": 3,
            "ascending": True,
        },
        {
            "method": "count_daily_series_days_after",
            "user_id": 42,
            "after_date": date(2026, 4, 20),
        },
    ]


def test_prophet_gateway_public_entrypoint_hides_model_state():
    gateway_params = inspect.signature(
        prophet_gateway.predict_bp_trend_for_user
    ).parameters
    lifecycle_params = inspect.signature(ProphetModelLifecycle).parameters

    assert list(gateway_params) == ["user_id", "forecast_days"]
    assert "predict_from_model_state" not in lifecycle_params
    assert not hasattr(prophet_gateway, "_predict_bp_trend_from_model_state")


def test_prophet_model_lifecycle_hides_inspect_then_predict_sequence():
    calls = []
    context = make_training_context("current-signature")
    model_context = SimpleNamespace(
        sys_model="sys-model",
        dia_model="dia-model",
        seasonality={"weekly_enabled": True, "monthly_enabled": False},
        model_cache_hit=True,
        model_asset_id=88,
        model_strategy="reuse_existing_model",
        model_data_signature="current-signature",
    )
    forecast = [{"day": 1, "systolic": 132.0, "diastolic": 84.0}]

    def inspect_model_state(user_id, forecast_days, repository=None):
        calls.append(("inspect", user_id, forecast_days, repository))
        return {
            "repository": repository,
            "context": context,
            "new_data_days_since_training": 1,
            "retrain_threshold_days": 3,
        }

    def load_or_train_models(user_id, forecast_days, repository, context, model_state):
        calls.append(
            ("load_or_train", user_id, forecast_days, repository, context, model_state)
        )
        return model_context

    def predict_from_models(sys_model, dia_model, forecast_days):
        calls.append(("forecast", sys_model, dia_model, forecast_days))
        return forecast

    def build_training_meta(model_context_payload, seasonality):
        calls.append(("training_meta", model_context_payload, seasonality))
        return {
            "confidence_level": "medium",
            "confidence_reasons": [],
        }

    repository = SimpleNamespace(name="repo")
    lifecycle = ProphetModelLifecycle(
        inspect_model_state=inspect_model_state,
        load_or_train_models=load_or_train_models,
        predict_from_models=predict_from_models,
        build_training_meta=build_training_meta,
        model_version="user-prophet-v-test",
    )

    result = lifecycle.predict(42, forecast_days=7, repository=repository)

    assert result["model_strategy"] == "reuse_existing_model"
    assert calls[0] == ("inspect", 42, 7, repository)
    assert calls[1][0:4] == ("load_or_train", 42, 7, repository)
    assert calls[1][4] == context
    assert calls[1][5]["new_data_days_since_training"] == 1
    assert calls[2] == ("forecast", "sys-model", "dia-model", 7)
    assert calls[3] == (
        "training_meta",
        context,
        {"weekly_enabled": True, "monthly_enabled": False},
    )


def test_prophet_model_lifecycle_builds_trend_prediction_from_model_state():
    repository = SimpleNamespace(name="repo")
    context = make_training_context("current-signature")
    model_context = SimpleNamespace(
        sys_model="sys-model",
        dia_model="dia-model",
        seasonality={"weekly_enabled": True, "monthly_enabled": False},
        model_cache_hit=False,
        model_asset_id=88,
        model_strategy="retrained_with_latest_data",
        model_data_signature="current-signature",
    )
    forecast = [{"day": 1, "systolic": 136.0, "diastolic": 86.0}]
    calls = []

    def inspect_model_state(user_id, forecast_days, repository=None):
        calls.append(("inspect", user_id, forecast_days, repository))
        return {
            "repository": repository,
            "context": context,
            "new_data_days_since_training": 4,
            "retrain_threshold_days": 3,
        }

    def load_or_train_models(user_id, forecast_days, repository, context, model_state):
        calls.append(
            ("load_or_train", user_id, forecast_days, repository, context, model_state)
        )
        return model_context

    def predict_from_models(sys_model, dia_model, forecast_days):
        calls.append(("forecast", sys_model, dia_model, forecast_days))
        return forecast

    def build_training_meta(model_context_payload, seasonality):
        calls.append(("training_meta", model_context_payload, seasonality))
        return {
            "confidence_level": "low",
            "confidence_reasons": ["insufficient_days"],
        }

    lifecycle = ProphetModelLifecycle(
        inspect_model_state=inspect_model_state,
        load_or_train_models=load_or_train_models,
        predict_from_models=predict_from_models,
        build_training_meta=build_training_meta,
        model_version="user-prophet-v-test",
    )

    result = lifecycle.predict(42, forecast_days=7, repository=repository)

    assert result["forecast"] == forecast
    assert result["data_days_used"] == 3
    assert result["total_history_days"] == 3
    assert result["data_range"] == "2026-04-20 ~ 2026-04-22"
    assert result["history_window_capped"] is False
    assert result["seasonality"] == {"weekly_enabled": True, "monthly_enabled": False}
    assert result["model_version"] == "user-prophet-v-test"
    assert result["model_strategy"] == "retrained_with_latest_data"
    assert result["model_asset_id"] == 88
    assert result["model_cache_hit"] is False
    assert result["data_signature"] == "current-signature"
    assert result["current_data_signature"] == "current-signature"
    assert result["training_meta"] == {
        "confidence_level": "low",
        "confidence_reasons": ["insufficient_days"],
        "model_strategy": "retrained_with_latest_data",
        "new_data_days_since_training": 4,
        "retrain_threshold_days": 3,
    }
    assert calls[0] == ("inspect", 42, 7, repository)
    assert calls[1][0:4] == ("load_or_train", 42, 7, repository)
    assert calls[2] == ("forecast", "sys-model", "dia-model", 7)
    assert calls[3] == (
        "training_meta",
        context,
        {"weekly_enabled": True, "monthly_enabled": False},
    )


def test_prophet_lifecycle_policy_reuses_only_before_retrain_threshold():
    active_model = SimpleNamespace(model_version=prophet_gateway.PROPHET_MODEL_VERSION)

    assert should_reuse_prophet_model(
        active_model,
        model_version=prophet_gateway.PROPHET_MODEL_VERSION,
        new_data_days_since_training=2,
        retrain_threshold_days=3,
    ) is True
    assert should_reuse_prophet_model(
        active_model,
        model_version=prophet_gateway.PROPHET_MODEL_VERSION,
        new_data_days_since_training=3,
        retrain_threshold_days=3,
    ) is False
    assert should_reuse_prophet_model(
        SimpleNamespace(model_version="old-version"),
        model_version=prophet_gateway.PROPHET_MODEL_VERSION,
        new_data_days_since_training=0,
        retrain_threshold_days=3,
    ) is False
    assert should_reuse_prophet_model(
        None,
        model_version=prophet_gateway.PROPHET_MODEL_VERSION,
        new_data_days_since_training=0,
        retrain_threshold_days=3,
    ) is False


def make_training_context(data_signature="current-signature"):
    return {
        "daily": pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2026-04-20", "2026-04-21", "2026-04-22"]
                ),
                "systolic": [132.0, 134.0, 136.0],
                "diastolic": [84.0, 85.0, 86.0],
                "measurements": [2, 2, 2],
            }
        ),
        "data_days_used": 3,
        "total_history_days": 3,
        "data_range": "2026-04-20 ~ 2026-04-22",
        "history_window_capped": False,
        "parameter_profile": "short",
        "avg_measurements_per_day": 2.0,
        "recent_sys_range_mean": 2.0,
        "recent_dia_range_mean": 1.0,
        "confidence_level": "low",
        "confidence_reasons": ["insufficient_days"],
        "data_signature": data_signature,
    }


def test_predict_bp_trend_reuses_loaded_active_model(monkeypatch):
    repository = SimpleNamespace()
    active_model = SimpleNamespace(id=77)
    context = make_training_context("current-signature")
    sys_model = FakeProphetModel("sys-reused")
    dia_model = FakeProphetModel("dia-reused")
    loaded_seasonality = {"weekly_enabled": True, "monthly_enabled": False}
    forecast = [{"day": 1, "systolic": 132.0, "diastolic": 84.0}]
    calls = {}

    def fake_load_models(model, cache_key):
        calls["load"] = (model, cache_key)
        return {
            "sys_model": sys_model,
            "dia_model": dia_model,
            "seasonality": loaded_seasonality,
        }

    def fake_predict(loaded_sys_model, loaded_dia_model, forecast_days):
        calls["predict"] = (loaded_sys_model, loaded_dia_model, forecast_days)
        return forecast

    def fail_build(*args, **kwargs):
        raise AssertionError("reuse path must not build Prophet models")

    monkeypatch.setattr(prophet_gateway, "_load_models_from_active_asset", fake_load_models)
    monkeypatch.setattr(prophet_gateway, "_predict_from_models", fake_predict)
    monkeypatch.setattr(prophet_gateway, "_build_prophet_model", fail_build)

    lifecycle = ProphetModelLifecycle(
        inspect_model_state=lambda *args, **kwargs: None,
        load_or_train_models=prophet_gateway._load_or_train_models,
        predict_from_models=prophet_gateway._predict_from_models,
        build_training_meta=prophet_gateway._build_training_meta,
        model_version=prophet_gateway.PROPHET_MODEL_VERSION,
    )

    result = lifecycle.predict_from_model_state(
        42,
        forecast_days=7,
        repository=repository,
        model_state={
            "repository": repository,
            "context": context,
            "active_model": active_model,
            "reuse_existing_model": True,
            "data_signature": "active-signature",
            "current_data_signature": "current-signature",
            "new_data_days_since_training": 1,
            "retrain_threshold_days": 3,
        },
    )

    assert calls["load"] == (
        active_model,
        (42, 7, prophet_gateway.PROPHET_MODEL_VERSION, "active-signature"),
    )
    assert calls["predict"] == (sys_model, dia_model, 7)
    assert result["forecast"] == forecast
    assert result["seasonality"] == loaded_seasonality
    assert result["model_cache_hit"] is True
    assert result["model_asset_id"] == 77
    assert result["model_strategy"] == "reuse_existing_model"
    assert result["data_signature"] == "active-signature"
    assert result["current_data_signature"] == "current-signature"
    assert result["training_meta"]["model_strategy"] == "reuse_existing_model"
    assert result["training_meta"]["new_data_days_since_training"] == 1
    assert result["training_meta"]["retrain_threshold_days"] == 3


def test_predict_bp_trend_trains_and_caches_when_reuse_disabled(monkeypatch):
    repository = SimpleNamespace()
    context = make_training_context("current-signature")
    forecast = [{"day": 1, "systolic": 136.0, "diastolic": 86.0}]
    model_cache = FakeModelCache()
    models = []
    calls = {}

    def fake_build_prophet_model(forecast_days, data_days_used, parameter_profile):
        model = FakeProphetModel(f"model-{len(models)}")
        models.append((model, forecast_days, data_days_used, parameter_profile))
        return model, {"weekly_enabled": False, "monthly_enabled": False}

    def fake_persist_model(
        model_repository,
        user_id,
        forecast_days,
        model_context,
        seasonality,
        sys_model,
        dia_model,
    ):
        calls["persist"] = (
            model_repository,
            user_id,
            forecast_days,
            model_context,
            seasonality,
            sys_model,
            dia_model,
        )
        return SimpleNamespace(id=88)

    def fake_predict(sys_model, dia_model, forecast_days):
        calls["predict"] = (sys_model, dia_model, forecast_days)
        return forecast

    monkeypatch.setattr(prophet_gateway, "_build_prophet_model", fake_build_prophet_model)
    monkeypatch.setattr(prophet_gateway, "_persist_user_model", fake_persist_model)
    monkeypatch.setattr(prophet_gateway, "_get_model_cache", lambda: model_cache)
    monkeypatch.setattr(prophet_gateway, "_predict_from_models", fake_predict)
    monkeypatch.setattr(
        prophet_gateway,
        "_load_models_from_active_asset",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("disabled reuse must not load active models")
        ),
    )

    lifecycle = ProphetModelLifecycle(
        inspect_model_state=lambda *args, **kwargs: None,
        load_or_train_models=prophet_gateway._load_or_train_models,
        predict_from_models=prophet_gateway._predict_from_models,
        build_training_meta=prophet_gateway._build_training_meta,
        model_version=prophet_gateway.PROPHET_MODEL_VERSION,
    )

    result = lifecycle.predict_from_model_state(
        42,
        forecast_days=7,
        repository=repository,
        model_state={
            "repository": repository,
            "context": context,
            "active_model": None,
            "reuse_existing_model": False,
            "data_signature": "current-signature",
            "current_data_signature": "current-signature",
            "new_data_days_since_training": 4,
            "retrain_threshold_days": 3,
        },
    )

    sys_model = models[0][0]
    dia_model = models[1][0]
    assert models[0][1:] == (7, 3, "short")
    assert models[1][1:] == (7, 3, "short")
    assert list(sys_model.fit_calls[0].columns) == ["ds", "y"]
    assert list(dia_model.fit_calls[0].columns) == ["ds", "y"]
    assert sys_model.fit_calls[0]["y"].tolist() == [132.0, 134.0, 136.0]
    assert dia_model.fit_calls[0]["y"].tolist() == [84.0, 85.0, 86.0]
    assert calls["persist"] == (
        repository,
        42,
        7,
        context,
        {"weekly_enabled": False, "monthly_enabled": False},
        sys_model,
        dia_model,
    )
    assert model_cache.set_calls == [
        (
            (42, 7, prophet_gateway.PROPHET_MODEL_VERSION, "current-signature"),
            {
                "sys_model": sys_model,
                "dia_model": dia_model,
                "seasonality": {"weekly_enabled": False, "monthly_enabled": False},
            },
        )
    ]
    assert calls["predict"] == (sys_model, dia_model, 7)
    assert result["forecast"] == forecast
    assert result["model_cache_hit"] is False
    assert result["model_asset_id"] == 88
    assert result["model_strategy"] == "retrained_with_latest_data"
    assert result["data_signature"] == "current-signature"
    assert result["training_meta"]["model_strategy"] == "retrained_with_latest_data"
    assert result["training_meta"]["new_data_days_since_training"] == 4
    assert result["training_meta"]["retrain_threshold_days"] == 3
