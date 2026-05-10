from datetime import datetime
import inspect
from types import SimpleNamespace

from prediction.application import prediction_run
from prediction.application.prediction_result_builder import (
    build_prediction_result,
    build_prediction_run_mode,
    build_save_payload,
)
from prediction.domain.guideline_signal_policy import (
    build_guideline_signal,
    derive_bp_grade,
    derive_guideline_trend_direction,
)
from prediction.schemas.commands import PredictCommand


def test_prediction_run_uses_domain_aggregation_policy():
    source = inspect.getsource(prediction_run)

    assert "prediction.infrastructure.prophet_gateway import AGGREGATION_MODE" not in source
    assert "from prediction.domain.run_key_policy import (" in source


def test_guideline_signal_policy_derives_bp_grade_and_trend_direction():
    fusion_meta = {
        "trend_summary": {
            "avg_sys": 162,
            "avg_dia": 92,
            "high_bp_days": 3,
            "sys_volatility": 6,
            "dia_volatility": 2,
        },
        "reasons": [],
    }

    signal = build_guideline_signal(
        risk_level_en="high",
        fusion_meta=fusion_meta,
        training_meta={"confidence_level": "medium"},
        data_days_used=12,
    )

    assert signal == {
        "risk_level": "high",
        "high_bp_days": 3,
        "trend_direction": "volatile",
        "record_days": 12,
        "confidence_level": "medium",
        "bp_grade": "grade2",
    }


def test_guideline_signal_policy_keeps_upward_and_bp_grade_thresholds_explicit():
    assert derive_guideline_trend_direction(
        fusion_meta={"trend_summary": {}, "reasons": ["upward_trend"]}
    ) == "upward"
    assert derive_guideline_trend_direction(
        fusion_meta={"trend_summary": {"sys_slope": 5, "dia_slope": 1}}
    ) == "upward"
    assert derive_guideline_trend_direction(
        fusion_meta={"trend_summary": {"sys_slope": 1, "dia_slope": 1}}
    ) == "stable"
    assert derive_bp_grade(181, 88) == "grade3"
    assert derive_bp_grade(160, 99) == "grade2"
    assert derive_bp_grade(140, 89) == "grade1"
    assert derive_bp_grade(120, 79) == "normal_high"
    assert derive_bp_grade(119, 79) == "normal"


def test_prediction_result_builder_keeps_model_reuse_and_payload_rules_together():
    command = PredictCommand(user_id=42, forecast_days=7)
    prophet_result = {
        "forecast": [{"day": 1, "systolic": 132, "diastolic": 84}],
        "data_days_used": 8,
        "total_history_days": 12,
        "history_window_capped": False,
        "data_range": "2026-04-01 ~ 2026-04-08",
        "seasonality": {"weekly_enabled": True},
        "model_strategy": "reuse_existing_model",
    }
    training_meta = {"confidence_level": "high", "confidence_reasons": ["enough_data"]}

    payload = build_save_payload(
        command=command,
        prophet_result=prophet_result,
        training_meta=training_meta,
        input_data={"age": 56},
        fusion_meta={"raw_probability": 0.31234},
        risk_probability=0.31234,
        risk_level="中风险",
        recommendations=[{"topic": "follow_up"}],
        prediction_run_key="run-key",
    )
    result = build_prediction_result(
        saved_prediction=(
            SimpleNamespace(id=901, created_at=datetime(2026, 5, 6, 21, 30)),
            None,
        ),
        risk_probability=0.31234,
        risk_level="中风险",
        risk_level_en="medium",
        risk_color="#d97706",
        prophet_result=prophet_result,
        command=command,
        training_meta=training_meta,
        recommendations=[{"topic": "follow_up"}],
        input_data={"age": 56},
        fusion_meta={"raw_probability": 0.31234},
        prediction_run_mode=build_prediction_run_mode(prophet_result, training_meta),
    )

    assert payload["risk_probability"] == 0.3123
    assert payload["cache_key"] == "run-key"
    assert payload["bp_forecast"] == prophet_result["forecast"]
    assert build_prediction_run_mode({}, training_meta) == "fresh_train"
    assert (
        build_prediction_run_mode({}, {"model_strategy": "reuse_existing_model"})
        == "model_reuse"
    )
    assert result.prediction_id == 901
    assert result.prophet_prediction_id is None
    assert result.cache_mode == "model_reuse"
    for legacy_result_cache_field in (
        "from_cache",
        "cached_at",
        "cache_expires_at",
        "result_cache_hours",
        "reuse_window_minutes",
    ):
        assert not hasattr(result, legacy_result_cache_field)
