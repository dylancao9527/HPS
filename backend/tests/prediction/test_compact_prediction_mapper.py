import importlib
from types import SimpleNamespace

import pytest

from prediction.infrastructure.compact_prediction_forecast_mapping import (
    build_forecast_points,
)
from prediction.infrastructure.compact_prediction_input_mapping import (
    build_input_snapshot,
)
from prediction.infrastructure.compact_prediction_mapper import (
    CompactPredictionMapper,
    CompactPredictionWriteMapper,
)
from prediction.infrastructure.compact_prediction_recommendation_mapping import (
    build_recommendations,
)
from prediction.infrastructure.compact_prediction_rows import CompactPredictionRows
from prediction.infrastructure.compact_prediction_training_mapping import (
    build_training_meta,
)
from prediction.infrastructure.prediction_payload_assembler import (
    PredictionPayloadAssembler,
)
from prediction.infrastructure.prediction_record_repository import (
    PredictionRecordRepository,
)
from prediction.infrastructure.repositories import PredictionRepository


def _compact_payload():
    return {
        "user_id": 42,
        "forecast_days": 7,
        "bp_forecast": [
            {
                "day": 1,
                "systolic": 132,
                "diastolic": 84,
                "systolic_lower": 126,
                "systolic_upper": 139,
                "diastolic_lower": 78,
                "diastolic_upper": 89,
            }
        ],
        "data_days_used": 8,
        "total_history_days": 12,
        "history_window_capped": False,
        "data_range": "2026-04-01 ~ 2026-04-08",
        "training_meta": {
            "aggregation_mode": "daily_mean",
            "parameter_profile": "standard",
            "seasonality": {
                "weekly_enabled": True,
                "monthly_enabled": False,
            },
            "confidence_level": "medium",
            "confidence_reasons": ["short_history"],
        },
        "input_data": {
            "age": 56,
            "male": 1,
            "currentSmoker": 1,
            "cigsPerDay": 5,
            "BPMeds": 1,
            "diabetes": 0,
            "totChol": 190,
            "sysBP": 138,
            "diaBP": 86,
            "BMI": 27.4,
            "heartRate": 72,
            "glucose": 96,
        },
        "fusion_meta": {
            "raw_probability": 0.3123,
            "fused_probability": 0.3923,
            "bp_meds_input": 1,
            "bp_meds_model_value": 0,
            "bp_meds_policy": "neutralized_for_conservative_inference",
            "medication_adjustment": 0.02,
            "reasons": ["high_bp_days", "upward_trend"],
        },
        "risk_probability": 0.3923,
        "risk_level": "中风险",
        "recommendations": [
            {
                "topic": "follow_up",
                "summary": "保持观察",
                "reason": "近期血压轻度波动",
                "actions": ["记录晨间血压"],
                "source_label": "指南库",
            }
        ],
    }


def test_compact_prediction_mapper_builds_compact_prediction_rows():
    rows = CompactPredictionWriteMapper.build_compact_prediction(_compact_payload())

    assert isinstance(rows, CompactPredictionRows)
    assert rows.prophet_prediction is None
    assert rows.prediction_record.user_id == 42
    assert rows.prediction_record.risk_probability == 0.3923
    assert rows.prediction_record.bp_forecast[0]["systolic"] == 132
    assert rows.prediction_record.training_meta["confidence_level"] == "medium"
    assert rows.prediction_record.recommendations[0]["summary"] == "保持观察"


def test_compact_mapper_does_not_expose_legacy_build_normalized_prediction_alias():
    assert not hasattr(CompactPredictionWriteMapper, "build_normalized_prediction")


def test_compact_mapper_build_input_snapshot_omits_legacy_cache_keys_for_new_payload():
    snapshot = CompactPredictionWriteMapper.build_input_snapshot(
        {
            "age": 56,
            "male": 1,
            "currentSmoker": 1,
            "cigsPerDay": 5,
            "BPMeds": 1,
            "diabetes": 0,
            "totChol": 190,
            "sysBP": 138,
            "diaBP": 86,
            "BMI": 27.4,
            "heartRate": 72,
            "glucose": 96,
            "_tot_chol_filled": True,
            "_glucose_filled": True,
            "_model_state_snapshot": {"model_version": "v1"},
            "_prediction_run_key": "run-key",
        }
    )

    assert snapshot["_model_state_snapshot"] == {"model_version": "v1"}
    assert snapshot["_prediction_run_key"] == "run-key"
    assert "_cache_snapshot" not in snapshot
    assert "_prophet_cache_key" not in snapshot


@pytest.mark.parametrize(
    "module_name",
    [
        "prediction.infrastructure.normalized_prediction_forecast_mapping",
        "prediction.infrastructure.normalized_prediction_fusion_mapping",
        "prediction.infrastructure.normalized_prediction_input_mapping",
        "prediction.infrastructure.normalized_prediction_mapper",
        "prediction.infrastructure.normalized_prediction_recommendation_mapping",
        "prediction.infrastructure.normalized_prediction_rows",
        "prediction.infrastructure.normalized_prediction_training_mapping",
        "prediction.infrastructure.backfill_normalized_storage",
    ],
)
def test_legacy_normalized_storage_modules_are_removed(module_name):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)


def test_prediction_infrastructure_defaults_to_compact_mapper():
    payloads = PredictionPayloadAssembler()
    records = PredictionRecordRepository(
        payload_assembler=SimpleNamespace(),
    )
    repository = PredictionRepository()

    assert isinstance(payloads.mapper, CompactPredictionMapper)
    assert isinstance(records.mapper, CompactPredictionMapper)
    assert isinstance(repository.mapper, CompactPredictionMapper)
