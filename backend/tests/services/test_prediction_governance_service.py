import csv
import io

from services.prediction_governance_service import PredictionGovernanceService


class FakeGovernanceRepository:
    def list_governance_predictions_for_export(self, **kwargs):
        self.export_filters = kwargs
        return [
            {
                "prediction_id": 901,
                "risk_level": "高风险",
                "risk_probability": 0.8123,
                "confidence_level": "low",
                "data_days_used": 2,
                "anomaly_flags": [
                    "high_risk_low_confidence",
                    "insufficient_data_prediction",
                ],
                "input_data": {
                    "age": 56,
                    "BMI": 27.4,
                    "BPMeds": 1,
                    "totChol": 190,
                    "glucose": 96,
                },
                "created_at": "2026-04-25T09:30:00",
            }
        ]


def test_governance_export_includes_prediction_chain_fields():
    repository = FakeGovernanceRepository()
    service = PredictionGovernanceService(repository=repository)

    csv_content = service.export_predictions_csv(anomaly_type="high_risk_low_confidence")
    rows = list(csv.DictReader(io.StringIO(csv_content)))

    assert repository.export_filters["anomaly_type"] == "high_risk_low_confidence"
    assert rows == [
        {
            "prediction_id": "901",
            "risk_level": "高风险",
            "risk_probability": "0.8123",
            "confidence_level": "low",
            "data_days_used": "2",
            "anomaly_flags": "high_risk_low_confidence|insufficient_data_prediction",
            "age": "56",
            "BMI": "27.4",
            "BPMeds": "1",
            "totChol": "190",
            "glucose": "96",
            "created_at": "2026-04-25T09:30:00",
        }
    ]
