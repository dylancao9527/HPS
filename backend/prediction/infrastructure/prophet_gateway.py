from dataclasses import dataclass
from typing import Any

from flask import current_app

from bp_series.repository import DailyBPSeriesRepository
from prediction.infrastructure.prophet_model_lifecycle import ProphetModelLifecycle
from prediction.infrastructure.prophet_model_cache import InMemoryProphetModelCache
from prediction.infrastructure.prophet_model_store import (
    LocalProphetModelStore,
    serialize_prophet_model,
    deserialize_prophet_model,
)
from prediction.infrastructure.prophet_lifecycle_policy import should_reuse_prophet_model
from prediction.infrastructure.prophet_trainer import (
    build_prophet_model as _build_prophet_model,
    predict_from_models as _predict_from_models,
)
from prediction.infrastructure.prophet_training_context import (
    AGGREGATION_MODE,
    MINIMUM_TRAIN_DAYS,
    build_daily_training_frame_from_series,
    build_training_context,
)
from prediction.infrastructure.repositories import PredictionRepository
from utils.time_utils import utc_now_naive

PROPHET_MODEL_VERSION = "user-prophet-v1"
_PROPHET_MODEL_CACHE = None


@dataclass
class ProphetModelContext:
    sys_model: Any
    dia_model: Any
    seasonality: dict[str, bool]
    model_cache_hit: bool
    model_asset_id: int
    model_strategy: str
    model_data_signature: str
    cache_key: tuple


def _get_model_store():
    return LocalProphetModelStore(current_app.config["PROPHET_MODEL_STORAGE_ROOT"])


def _get_model_cache():
    global _PROPHET_MODEL_CACHE
    if _PROPHET_MODEL_CACHE is None:
        _PROPHET_MODEL_CACHE = InMemoryProphetModelCache(
            ttl_seconds=current_app.config["PROPHET_MEMORY_CACHE_TTL_SECONDS"],
            max_entries=128,
        )
    return _PROPHET_MODEL_CACHE


def clear_prophet_model_cache():
    global _PROPHET_MODEL_CACHE
    _PROPHET_MODEL_CACHE = None


def _build_model_cache_key(user_id, forecast_days, data_signature):
    return (user_id, forecast_days, PROPHET_MODEL_VERSION, data_signature)


def _load_daily_records(user_id, *, max_train_days=None, daily_series_repository=None):
    daily_series_repository = daily_series_repository or DailyBPSeriesRepository()
    total_days = daily_series_repository.count_daily_series_days(user_id=user_id)

    if total_days == 0:
        raise ValueError(f"没有血压记录，请先录入至少{MINIMUM_TRAIN_DAYS}天的血压数据")

    if total_days < MINIMUM_TRAIN_DAYS:
        raise ValueError(
            f"血压数据不足：仅有 {total_days} 天记录，至少需要{MINIMUM_TRAIN_DAYS}天数据才能进行预测"
        )

    if max_train_days:
        points = daily_series_repository.load_recent_daily_series(
            user_id=user_id,
            limit=max_train_days,
            ascending=True,
        )
    else:
        points = daily_series_repository.load_daily_series(
            user_id=user_id,
            ascending=True,
        )

    daily = build_daily_training_frame_from_series(points)
    return daily, total_days


def _build_training_meta(context, seasonality):
    return {
        "aggregation_mode": AGGREGATION_MODE,
        "parameter_profile": context["parameter_profile"],
        "seasonality": seasonality,
        "avg_measurements_per_day": context["avg_measurements_per_day"],
        "recent_sys_range_mean": context["recent_sys_range_mean"],
        "recent_dia_range_mean": context["recent_dia_range_mean"],
        "confidence_level": context["confidence_level"],
        "confidence_reasons": context["confidence_reasons"],
    }


def _load_models_from_active_asset(active_model, cache_key):
    if not active_model:
        return None
    if active_model.model_version != PROPHET_MODEL_VERSION:
        return None
    if active_model.data_signature != cache_key[3]:
        return None
    if not active_model.storage_key:
        return None

    cache = _get_model_cache()
    cached = cache.get(cache_key)
    if cached:
        return cached

    store = _get_model_store()
    if not store.exists(active_model.storage_key):
        return None

    bundle = store.read_bundle(active_model.storage_key)
    loaded = {
        "sys_model": deserialize_prophet_model(bundle.sys_model_blob),
        "dia_model": deserialize_prophet_model(bundle.dia_model_blob),
        "seasonality": {
            "weekly_enabled": active_model.weekly_enabled,
            "monthly_enabled": active_model.monthly_enabled,
        },
    }
    cache.set(cache_key, loaded)
    return loaded


def _persist_user_model(repository, user_id, forecast_days, context, seasonality, sys_model, dia_model):
    store = _get_model_store()
    storage_key = store.build_storage_key(
        user_id=user_id,
        forecast_days=forecast_days,
        model_version=PROPHET_MODEL_VERSION,
        data_signature=context["data_signature"],
    )
    sys_blob = serialize_prophet_model(sys_model)
    dia_blob = serialize_prophet_model(dia_model)
    store.write_bundle(storage_key, sys_blob, dia_blob)
    return repository.save_user_prophet_model(
        {
            "user_id": user_id,
            "forecast_days": forecast_days,
            "model_version": PROPHET_MODEL_VERSION,
            "data_signature": context["data_signature"],
            "aggregation_mode": AGGREGATION_MODE,
            "trained_at": utc_now_naive(),
            "trained_until": context["daily"]["date"].max().date(),
            "data_days_used": context["data_days_used"],
            "total_history_days": context["total_history_days"],
            "history_window_capped": context["history_window_capped"],
            "parameter_profile": context["parameter_profile"],
            "weekly_enabled": seasonality["weekly_enabled"],
            "monthly_enabled": seasonality["monthly_enabled"],
            "storage_key": storage_key,
        }
    )



def _train_models_for_context(forecast_days, context):
    """Train Prophet models via gateway-level _build_prophet_model (monkeypatchable)."""
    sys_df = context["daily"][["date", "systolic"]].rename(
        columns={"date": "ds", "systolic": "y"}
    )
    sys_model, seasonality = _build_prophet_model(
        forecast_days, context["data_days_used"], context["parameter_profile"]
    )
    sys_model.fit(sys_df)

    dia_df = context["daily"][["date", "diastolic"]].rename(
        columns={"date": "ds", "diastolic": "y"}
    )
    dia_model, _ = _build_prophet_model(
        forecast_days, context["data_days_used"], context["parameter_profile"]
    )
    dia_model.fit(dia_df)

    return sys_model, dia_model, seasonality


def _load_or_train_models(user_id, forecast_days, repository, context, model_state):
    active_model = model_state["active_model"]
    reuse_existing_model = bool(model_state.get("reuse_existing_model"))
    model_data_signature = model_state.get("data_signature") or context["data_signature"]
    cache_key = _build_model_cache_key(user_id, forecast_days, model_data_signature)
    loaded_models = (
        _load_models_from_active_asset(active_model, cache_key)
        if reuse_existing_model
        else None
    )

    if loaded_models:
        return ProphetModelContext(
            sys_model=loaded_models["sys_model"],
            dia_model=loaded_models["dia_model"],
            seasonality=loaded_models["seasonality"],
            model_cache_hit=True,
            model_asset_id=active_model.id,
            model_strategy="reuse_existing_model",
            model_data_signature=model_data_signature,
            cache_key=cache_key,
        )

    sys_model, dia_model, seasonality = _train_models_for_context(
        forecast_days, context
    )
    model_asset = _persist_user_model(
        repository,
        user_id,
        forecast_days,
        context,
        seasonality,
        sys_model,
        dia_model,
    )
    model_data_signature = context["data_signature"]
    cache_key = _build_model_cache_key(user_id, forecast_days, model_data_signature)
    _get_model_cache().set(
        cache_key,
        {
            "sys_model": sys_model,
            "dia_model": dia_model,
            "seasonality": seasonality,
        },
    )
    return ProphetModelContext(
        sys_model=sys_model,
        dia_model=dia_model,
        seasonality=seasonality,
        model_cache_hit=False,
        model_asset_id=model_asset.id,
        model_strategy="retrained_with_latest_data",
        model_data_signature=model_data_signature,
        cache_key=cache_key,
    )


def inspect_prophet_model_state_for_user(user_id, forecast_days=7, repository=None):
    repository = repository or PredictionRepository()
    max_train_days = current_app.config.get("PROPHET_MAX_TRAIN_DAYS", 90)
    daily_series_repository = DailyBPSeriesRepository()
    daily, total_days = _load_daily_records(
        user_id,
        max_train_days=max_train_days,
        daily_series_repository=daily_series_repository,
    )
    context = build_training_context(
        daily,
        total_days=total_days,
        forecast_days=forecast_days,
        max_train_days=max_train_days,
        model_version=PROPHET_MODEL_VERSION,
    )
    active_model = repository.get_active_prophet_model(user_id, forecast_days)
    retrain_threshold_days = max(
        1,
        int(current_app.config.get("PROPHET_RETRAIN_AFTER_DAYS", 3)),
    )
    new_data_days_since_training = daily_series_repository.count_daily_series_days_after(
        user_id=user_id,
        after_date=active_model.trained_until if active_model else None,
    )
    reuse_existing_model = should_reuse_prophet_model(
        active_model,
        model_version=PROPHET_MODEL_VERSION,
        new_data_days_since_training=new_data_days_since_training,
        retrain_threshold_days=retrain_threshold_days,
    )
    model_data_signature = (
        active_model.data_signature if reuse_existing_model else context["data_signature"]
    )
    cache_key = _build_model_cache_key(user_id, forecast_days, model_data_signature)
    model_cache_hit = bool(
        reuse_existing_model and _load_models_from_active_asset(active_model, cache_key)
    )
    return {
        "repository": repository,
        "context": context,
        "active_model": active_model,
        "model_cache_hit": model_cache_hit,
        "model_version": PROPHET_MODEL_VERSION,
        "data_signature": model_data_signature,
        "current_data_signature": context["data_signature"],
        "reuse_existing_model": reuse_existing_model,
        "new_data_days_since_training": new_data_days_since_training,
        "retrain_threshold_days": retrain_threshold_days,
    }


def _build_prophet_model_lifecycle():
    return ProphetModelLifecycle(
        inspect_model_state=inspect_prophet_model_state_for_user,
        load_or_train_models=_load_or_train_models,
        predict_from_models=_predict_from_models,
        build_training_meta=_build_training_meta,
        model_version=PROPHET_MODEL_VERSION,
    )


def predict_bp_trend_for_user(user_id, forecast_days=7):
    return _build_prophet_model_lifecycle().predict(
        user_id,
        forecast_days=forecast_days,
    )
