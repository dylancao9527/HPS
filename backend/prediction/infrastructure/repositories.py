from models import (
    BPRecord,
    PredictionRecord,
    User,
    UserProphetModel,
)
from prediction.infrastructure.bp_data_repository import BPDataRepository
from prediction.infrastructure.compact_prediction_mapper import (
    CompactPredictionMapper,
)
from prediction.infrastructure.prediction_governance_repository import (
    PredictionGovernanceRepository,
)
from prediction.infrastructure.prediction_payload_assembler import (
    PredictionPayloadAssembler,
)
from prediction.infrastructure.prediction_record_repository import (
    PredictionRecordRepository,
)
from prediction.infrastructure.prophet_model_repository import ProphetModelRepository


class PredictionRepository:
    user_model = User
    bp_record_model = BPRecord
    prediction_model = PredictionRecord
    user_prophet_model = UserProphetModel

    def __init__(
        self,
        *,
        mapper=None,
        payloads=None,
        prophet_models=None,
        records=None,
        governance=None,
        bp_data=None,
    ):
        mapper = mapper or CompactPredictionMapper()
        self.payloads = payloads or PredictionPayloadAssembler(mapper=mapper)
        self.prophet_models = prophet_models or ProphetModelRepository()
        self.records = records or PredictionRecordRepository(
            payload_assembler=self.payloads,
            mapper=mapper,
        )
        self.governance = governance or PredictionGovernanceRepository(
            payload_assembler=self.payloads
        )
        self.bp_data = bp_data or BPDataRepository()

    @property
    def mapper(self):
        return self.payloads.mapper

    @mapper.setter
    def mapper(self, value):
        self.payloads.mapper = value
        if hasattr(self.records, "mapper"):
            self.records.mapper = value

    def get_user(self, user_id):
        return self.bp_data.get_user(user_id)

    def get_latest_bp_record(self, user_id):
        return self.bp_data.get_latest_bp_record(user_id)

    def get_active_prophet_model(self, user_id, forecast_days):
        return self.prophet_models.get_active_prophet_model(user_id, forecast_days)

    def save_user_prophet_model(self, payload):
        return self.prophet_models.save_user_prophet_model(payload)

    def list_prophet_models_with_legacy_blobs(self, *, limit: int):
        return self.prophet_models.list_prophet_models_with_legacy_blobs(limit=limit)

    def update_prophet_storage_key(self, *, row_id: int, storage_key: str):
        return self.prophet_models.update_prophet_storage_key(
            row_id=row_id,
            storage_key=storage_key,
        )

    def list_prophet_storage_keys(self) -> list[str]:
        return self.prophet_models.list_prophet_storage_keys()

    def commit(self):
        return self.prophet_models.commit()

    def prune_inactive_prophet_models(
        self, *, keep_inactive_per_slot: int, max_inactive_age_hours: int
    ):
        return self.prophet_models.prune_inactive_prophet_models(
            keep_inactive_per_slot=keep_inactive_per_slot,
            max_inactive_age_hours=max_inactive_age_hours,
        )

    def assemble_prediction_payload(self, item, prophet_record=None):
        return self.payloads.assemble_prediction_payload(
            item,
            prophet_record=prophet_record,
        )

    def get_prediction_history(
        self, *, user_id, page, per_page, start_date="", end_date=""
    ):
        return self.records.get_prediction_history(
            user_id=user_id,
            page=page,
            per_page=per_page,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def _is_high_risk(risk_level):
        return PredictionGovernanceRepository.is_high_risk(risk_level)

    @staticmethod
    def _build_anomaly_flags(payload):
        return PredictionGovernanceRepository.build_anomaly_flags(payload)

    def _governance_base_query(self):
        return self.governance.governance_base_query()

    @staticmethod
    def _high_risk_condition():
        return PredictionGovernanceRepository.high_risk_condition()

    @staticmethod
    def _without_recommendation_condition():
        return PredictionGovernanceRepository.without_recommendation_condition()

    def _apply_governance_filters(
        self,
        query,
        *,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
    ):
        return self.governance.apply_governance_filters(
            query,
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
        )

    def _assemble_governance_record(self, item, prophet_record=None):
        return self.governance.assemble_governance_record(
            item,
            prophet_record=prophet_record,
        )

    @staticmethod
    def _build_governance_list_row(row):
        return PredictionGovernanceRepository.build_governance_list_row(row)

    def get_governance_summary(self):
        return self.governance.get_governance_summary()

    def list_governance_predictions(
        self,
        *,
        page,
        per_page,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        return self.governance.list_governance_predictions(
            page=page,
            per_page=per_page,
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )

    def list_governance_predictions_for_export(
        self,
        *,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        return self.governance.list_governance_predictions_for_export(
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )

    def get_governance_prediction_detail(self, prediction_id):
        return self.governance.get_governance_prediction_detail(prediction_id)

    def delete_prediction(self, *, user_id, prediction_id):
        return self.records.delete_prediction(
            user_id=user_id,
            prediction_id=prediction_id,
        )

    def batch_delete_predictions(self, *, user_id, prediction_ids):
        return self.records.batch_delete_predictions(
            user_id=user_id,
            prediction_ids=prediction_ids,
        )

    def list_prediction_trend(self, *, user_id, limit):
        return self.records.list_prediction_trend(user_id=user_id, limit=limit)

    def get_bp_data_status(self, *, user_id, forecast_days):
        return self.bp_data.get_bp_data_status(
            user_id=user_id,
            forecast_days=forecast_days,
        )

    def save_prediction(self, payload):
        return self.records.save_prediction(payload)
