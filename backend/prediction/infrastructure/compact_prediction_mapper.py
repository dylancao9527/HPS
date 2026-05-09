from models import PredictionRecord
from prediction.domain.governance_policy import build_anomaly_flags
from prediction.infrastructure.compact_prediction_forecast_mapping import (
    assemble_forecast,
    build_forecast_points,
)
from prediction.infrastructure.compact_prediction_fusion_mapping import (
    assemble_fusion_meta,
    build_fusion_meta,
)
from prediction.infrastructure.compact_prediction_input_mapping import (
    assemble_input_data,
    build_input_snapshot,
)
from prediction.infrastructure.compact_prediction_recommendation_mapping import (
    PredictionGuidelineMapping,
    assemble_recommendations,
    build_recommendations,
)
from prediction.infrastructure.compact_prediction_rows import (
    CompactPredictionRows,
)
from prediction.infrastructure.compact_prediction_training_mapping import (
    assemble_training_meta,
    build_confidence_reasons,
    build_training_meta,
)


class CompactPredictionWriteMapper(PredictionGuidelineMapping):
    build_input_snapshot = staticmethod(build_input_snapshot)
    build_fusion_meta = staticmethod(build_fusion_meta)
    build_confidence_reasons = staticmethod(build_confidence_reasons)
    build_recommendations = staticmethod(build_recommendations)
    build_forecast_points = staticmethod(build_forecast_points)
    build_training_meta = staticmethod(build_training_meta)

    @classmethod
    def build_compact_prediction(cls, payload):
        training_meta = cls.build_training_meta(payload.get("training_meta", {}))
        training_meta.update(
            {
                "forecast_days": payload["forecast_days"],
                "total_history_days": payload["total_history_days"],
                "history_window_capped": payload["history_window_capped"],
                "data_range": payload["data_range"],
            }
        )
        fusion_meta = payload.get("fusion_meta", {}) or {}
        cache_mode = (
            "model_reuse"
            if training_meta.get("model_strategy") == "reuse_existing_model"
            else "fresh_train"
        )
        input_snapshot = cls.build_input_snapshot(payload["input_data"])
        bp_forecast = cls.build_forecast_points(payload["bp_forecast"])
        stored_fusion_meta = cls.build_fusion_meta(fusion_meta)
        recommendations = cls.build_recommendations(payload.get("recommendations", []))
        confidence_level = training_meta.get("confidence_level")
        anomaly_payload = {
            "risk_level": payload["risk_level"],
            "recommendations": recommendations,
            "data_days_used": payload["data_days_used"],
            "confidence_level": confidence_level,
            "input_data": input_snapshot,
            "bp_forecast": bp_forecast,
            "cache_mode": cache_mode,
        }
        anomaly_flags = build_anomaly_flags(anomaly_payload)

        prediction_record = PredictionRecord(
            user_id=payload["user_id"],
            risk_probability=payload["risk_probability"],
            risk_level=payload["risk_level"],
            data_days_used=payload["data_days_used"],
            confidence_level=confidence_level,
            cache_mode=cache_mode,
            has_anomaly=bool(anomaly_flags),
            input_snapshot=input_snapshot,
            fusion_meta=stored_fusion_meta,
            bp_forecast=bp_forecast,
            training_meta=training_meta,
            recommendations=recommendations,
            anomaly_flags=anomaly_flags,
        )
        return CompactPredictionRows(prediction_record=prediction_record)

class CompactPredictionReadMapper(PredictionGuidelineMapping):
    assemble_input_data = staticmethod(assemble_input_data)
    assemble_fusion_meta = staticmethod(assemble_fusion_meta)
    assemble_recommendations = staticmethod(assemble_recommendations)
    assemble_forecast = staticmethod(assemble_forecast)
    assemble_training_meta = staticmethod(assemble_training_meta)


class CompactPredictionMapper(CompactPredictionWriteMapper, CompactPredictionReadMapper):
    pass


__all__ = [
    "CompactPredictionMapper",
    "CompactPredictionReadMapper",
    "CompactPredictionRows",
    "CompactPredictionWriteMapper",
    "PredictionGuidelineMapping",
]
