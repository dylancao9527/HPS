from prediction.infrastructure.compact_prediction_mapper import (
    CompactPredictionMapper,
)


class PredictionPayloadAssembler:
    def __init__(self, mapper=None):
        self.mapper = mapper or CompactPredictionMapper()

    def assemble_prediction_payload(self, item, prophet_record=None):
        training_meta = self.mapper.assemble_training_meta(prophet_record, item)
        row = item.to_dict()
        row["id"] = item.id
        row["prediction_id"] = item.id
        row["created_at"] = item.created_at.isoformat() if item.created_at else None
        row["input_data"] = self.mapper.assemble_input_data(
            item, prophet_record=prophet_record
        )
        row["fusion_meta"] = self.mapper.assemble_fusion_meta(
            item, prophet_record=prophet_record
        )
        row["bp_forecast"] = self.mapper.assemble_forecast(prophet_record, item)
        row["recommendations"] = self.mapper.assemble_recommendations(item)
        row["training_meta"] = training_meta
        row["seasonality"] = training_meta.get("seasonality", {})
        row["confidence_level"] = training_meta.get("confidence_level")
        row["confidence_reasons"] = training_meta.get("confidence_reasons", [])
        row["cache_mode"] = getattr(item, "cache_mode", None) or (
            "model_reuse"
            if training_meta.get("model_strategy") == "reuse_existing_model"
            else "fresh_train"
        )
        row["forecast_days"] = training_meta.get("forecast_days", 7)
        row["data_days_used"] = getattr(item, "data_days_used", None)
        row["total_history_days"] = training_meta.get("total_history_days")
        row["history_window_capped"] = training_meta.get("history_window_capped")
        row["data_range"] = training_meta.get("data_range")
        row["prophet_prediction_id"] = None
        row["anomaly_flags"] = getattr(item, "anomaly_flags", None) or []
        return row
