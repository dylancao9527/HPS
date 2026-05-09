from prediction.infrastructure.prediction_governance_read_model import (
    GovernanceProjection,
    PredictionGovernanceReadModel,
)


class PredictionGovernanceRepository:
    def __init__(self, payload_assembler, read_model=None):
        self.payload_assembler = payload_assembler
        self.read_model = read_model or PredictionGovernanceReadModel(
            payload_assembler=payload_assembler
        )

    @staticmethod
    def is_high_risk(risk_level):
        return PredictionGovernanceReadModel.is_high_risk(risk_level)

    @staticmethod
    def build_anomaly_flags(payload):
        return PredictionGovernanceReadModel.build_anomaly_flags(payload)

    def governance_base_query(self):
        return self.read_model.governance_base_query()

    @staticmethod
    def high_risk_condition():
        return PredictionGovernanceReadModel.high_risk_condition()

    @staticmethod
    def without_recommendation_condition():
        return PredictionGovernanceReadModel.without_recommendation_condition()

    def apply_governance_filters(
        self,
        query,
        *,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
    ):
        _ = has_anomaly
        return self.read_model.apply_governance_filters(
            query,
            risk_level=risk_level,
            confidence_level=confidence_level,
        )

    @staticmethod
    def filter_by_anomaly_state(rows, *, has_anomaly=None, anomaly_type=""):
        return PredictionGovernanceReadModel.filter_by_anomaly_state(
            rows,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )

    @staticmethod
    def paginate_rows(rows, *, page, per_page):
        return PredictionGovernanceReadModel.paginate_rows(
            rows,
            page=page if page > 0 else 1,
            per_page=per_page if per_page > 0 else 20,
        )

    def assemble_governance_record(self, item, prophet_record=None):
        return self.read_model.projection.assemble_record(
            item,
            prophet_record=prophet_record,
        )

    @staticmethod
    def build_governance_list_row(row):
        return GovernanceProjection.build_list_row(row)

    def get_governance_summary(self):
        return self.read_model.get_summary()

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
        return self.read_model.list_predictions(
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
        return self.read_model.list_predictions_for_export(
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )

    def get_governance_prediction_detail(self, prediction_id):
        return self.read_model.get_prediction_detail(prediction_id)
