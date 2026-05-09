import csv
import io

from prediction.infrastructure.repositories import PredictionRepository


class PredictionGovernanceService:
    def __init__(self, repository=None):
        self.repository = repository or PredictionRepository()

    def get_summary(self):
        return self.repository.get_governance_summary()

    def list_predictions(
        self,
        *,
        page=1,
        per_page=20,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        return self.repository.list_governance_predictions(
            page=page,
            per_page=per_page,
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )

    def get_prediction_detail(self, prediction_id):
        return self.repository.get_governance_prediction_detail(prediction_id)

    def export_predictions_csv(
        self,
        *,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        records = self.repository.list_governance_predictions_for_export(
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "prediction_id",
                "risk_level",
                "risk_probability",
                "confidence_level",
                "data_days_used",
                "anomaly_flags",
                "age",
                "BMI",
                "BPMeds",
                "totChol",
                "glucose",
                "created_at",
            ]
        )

        for row in records:
            input_data = row.get("input_data") or {}
            writer.writerow(
                [
                    row.get("prediction_id"),
                    row.get("risk_level"),
                    row.get("risk_probability"),
                    row.get("confidence_level"),
                    row.get("data_days_used"),
                    "|".join(row.get("anomaly_flags") or []),
                    input_data.get("age"),
                    input_data.get("BMI"),
                    input_data.get("BPMeds"),
                    input_data.get("totChol"),
                    input_data.get("glucose"),
                    row.get("created_at"),
                ]
            )

        return output.getvalue()
