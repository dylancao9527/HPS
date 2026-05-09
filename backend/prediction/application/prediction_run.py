from prediction.application.prediction_result_builder import (
    build_prediction_result,
    build_prediction_run_mode,
    build_save_payload,
)
from prediction.domain.bp_data_policy import require_minimum_bp_days_for_prediction
from prediction.domain.guideline_signal_policy import build_guideline_signal
from prediction.domain.run_key_policy import build_prediction_run_key
from prediction.domain.trend_policy import fuse_risk_with_trend
from prediction.infrastructure.prophet_gateway import AGGREGATION_MODE
from prediction.schemas.input_snapshot import PredictionInputSnapshot


class PredictionRun:
    def __init__(
        self,
        *,
        repository,
        prophet_gateway,
        risk_gateway,
        recommendation_service,
        risk_level_service,
        now_provider,
    ):
        self.repository = repository
        self.prophet_gateway = prophet_gateway
        self.risk_gateway = risk_gateway
        self.recommendation_service = recommendation_service
        self.risk_level_service = risk_level_service
        self.now_provider = now_provider

    def execute(self, command):
        user = self.repository.get_user(command.user_id)
        latest_bp = self.repository.get_latest_bp_record(command.user_id)
        input_snapshot = PredictionInputSnapshot.from_user_and_latest_bp(
            user=user,
            latest_bp=latest_bp,
        )
        risk_inputs = input_snapshot.to_model_input()
        bp_data_status = self.repository.get_bp_data_status(
            user_id=command.user_id,
            forecast_days=command.forecast_days,
        )
        require_minimum_bp_days_for_prediction(bp_data_status)

        prophet_result = self.prophet_gateway.predict(
            command.user_id,
            command.forecast_days,
        )
        model_state = self._build_model_state(prophet_result)
        prediction_run_key = build_prediction_run_key(
            user_id=command.user_id,
            forecast_days=command.forecast_days,
            model_version=model_state.get("model_version"),
            data_signature=model_state.get("data_signature"),
            aggregation_mode=AGGREGATION_MODE,
            risk_inputs=risk_inputs,
        )
        input_data = input_snapshot.to_persistence_payload(
            model_state=model_state,
            prediction_run_key=prediction_run_key,
        )

        (
            risk_probability,
            risk_level,
            risk_level_en,
            risk_color,
            fusion_meta,
        ) = self._score_and_fuse_risk(
            risk_inputs=risk_inputs,
            prophet_result=prophet_result,
            use_trend_fusion=getattr(command, "use_trend_fusion", True),
        )
        training_meta = prophet_result.get("training_meta", {})
        guideline_signal = build_guideline_signal(
            risk_level_en=risk_level_en,
            fusion_meta=fusion_meta,
            training_meta=training_meta,
            data_days_used=prophet_result["data_days_used"],
        )
        recommendations = self.recommendation_service.generate(
            guideline_signal=guideline_signal,
            risk_probability=risk_probability,
        )
        prediction_run_mode = build_prediction_run_mode(
            prophet_result,
            training_meta,
        )
        payload = build_save_payload(
            command=command,
            prophet_result=prophet_result,
            training_meta=training_meta,
            input_data=input_data,
            fusion_meta=fusion_meta,
            risk_probability=risk_probability,
            risk_level=risk_level,
            recommendations=recommendations,
            prediction_run_key=prediction_run_key,
        )
        saved_prediction = self.repository.save_prediction(payload)
        return build_prediction_result(
            saved_prediction=saved_prediction,
            risk_probability=risk_probability,
            risk_level=risk_level,
            risk_level_en=risk_level_en,
            risk_color=risk_color,
            prophet_result=prophet_result,
            command=command,
            training_meta=training_meta,
            recommendations=recommendations,
            input_data=input_data,
            fusion_meta=fusion_meta,
            prediction_run_mode=prediction_run_mode,
        )

    def _build_model_state(self, prophet_result):
        return {
            "model_version": prophet_result.get("model_version"),
            "data_signature": prophet_result.get("data_signature"),
            "model_cache_hit": prophet_result.get("model_cache_hit"),
        }

    def _score_and_fuse_risk(self, *, risk_inputs, prophet_result, use_trend_fusion):
        raw_probability, inference_meta = self.risk_gateway.score(
            risk_inputs, prophet_result["forecast"]
        )
        fusion_meta = {
            **fuse_risk_with_trend(
                raw_probability,
                prophet_result["forecast"],
                bp_meds=risk_inputs.get("BPMeds"),
            ),
            **inference_meta,
        }
        if not use_trend_fusion:
            fusion_meta["fused_probability"] = raw_probability
            fusion_meta["trend_adjustment"] = 0.0
            fusion_meta["medication_adjustment"] = 0.0
        risk_probability = fusion_meta["fused_probability"]
        risk_level, risk_level_en, risk_color = self.risk_level_service.get_level(
            risk_probability
        )
        return risk_probability, risk_level, risk_level_en, risk_color, fusion_meta
