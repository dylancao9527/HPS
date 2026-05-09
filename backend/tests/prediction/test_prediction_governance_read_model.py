from types import SimpleNamespace

from sqlalchemy.dialects import mysql

import prediction.infrastructure.prediction_governance_read_model as read_model_module
from models import PredictionRecord
from prediction.infrastructure.prediction_governance_read_model import (
    KNOWN_ANOMALY_TYPES,
    PredictionGovernanceReadModel,
)


class FakeProjection:
    def __init__(self):
        self.assembled = []

    def assemble_record(self, item, prophet_record=None):
        _ = prophet_record
        self.assembled.append(item)
        return item

    @staticmethod
    def build_list_row(row):
        return row


class CompactAnomalyQuery:
    def __init__(self):
        self.filters = []
        self.paginate_kwargs = None
        self.all_calls = 0

    def filter(self, *conditions):
        self.filters.extend(conditions)
        return self

    def paginate(self, **kwargs):
        self.paginate_kwargs = kwargs
        return SimpleNamespace(
            items=[
                {
                    "prediction_id": 901,
                    "risk_level": "高风险",
                    "anomaly_flags": ["high_risk_low_confidence"],
                }
            ],
            total=1,
            pages=1,
        )

    def all(self):
        self.all_calls += 1
        return [
            {
                "prediction_id": 901,
                "risk_level": "高风险",
                "anomaly_flags": ["high_risk_low_confidence"],
            }
        ]


def test_anomaly_type_condition_uses_mysql_json_contains():
    condition = PredictionGovernanceReadModel.anomaly_condition_for_type(
        "high_risk_low_confidence"
    )

    compiled = condition.compile(dialect=mysql.dialect())

    assert "json_contains" in str(compiled).lower()
    assert "has_anomaly" not in str(compiled).lower()
    assert compiled.params["json_contains_1"] == '"high_risk_low_confidence"'
    assert compiled.params["json_contains_2"] == "$"


def test_governance_anomaly_type_filter_uses_database_json_projection():
    query = CompactAnomalyQuery()

    class ReadModel(PredictionGovernanceReadModel):
        def governance_base_query(self):
            return query

    read_model = ReadModel(payload_assembler=None, projection=FakeProjection())

    result = read_model.list_predictions(
        page=1,
        per_page=20,
        has_anomaly=True,
        anomaly_type="high_risk_low_confidence",
    )

    assert query.filters
    assert "json_contains" in str(query.filters[0]).lower()
    assert query.paginate_kwargs == {
        "page": 1,
        "per_page": 20,
        "error_out": False,
    }
    assert query.all_calls == 0
    assert result["records"] == [
        {
            "prediction_id": 901,
            "risk_level": "高风险",
            "anomaly_flags": ["high_risk_low_confidence"],
        }
    ]


def test_governance_summary_uses_database_metrics_without_payload_projection():
    expected = {
        "total_predictions": 2,
        "risk_distribution": {"高风险": 1, "低风险": 1},
        "confidence_distribution": {"low": 1, "high": 1},
        "anomaly_counts": {"high_risk_low_confidence": 1},
        "high_risk_predictions": 1,
        "low_confidence_predictions": 1,
        "low_confidence_rate": 0.5,
        "anomaly_predictions": 1,
        "insufficient_data_predictions": 0,
        "prophet_model_reuse_count": 0,
        "prophet_model_retrain_count": 2,
    }

    class ExplodingProjection(FakeProjection):
        def assemble_record(self, item, prophet_record=None):
            raise AssertionError("summary should not assemble full governance payloads")

    class ReadModel(PredictionGovernanceReadModel):
        def _build_summary_from_database(self):
            return expected

    read_model = ReadModel(payload_assembler=None, projection=ExplodingProjection())

    assert read_model.get_summary() == expected


def test_governance_summary_counts_known_anomalies_without_scanning_json_flags(
    monkeypatch,
):
    db_session = RecordingSummarySession()
    monkeypatch.setattr(
        read_model_module,
        "db",
        SimpleNamespace(session=db_session),
    )

    class ReadModel(PredictionGovernanceReadModel):
        def __init__(self):
            super().__init__(payload_assembler=None, projection=FakeProjection())
            self.count_conditions = []
            self.count_values = iter(
                [
                    5,
                    1,
                    2,
                    3,
                    4,
                    5,
                    2,
                    1,
                    4,
                    2,
                ]
            )

        def _count_predictions_where(self, *conditions):
            self.count_conditions.append(conditions)
            return next(self.count_values)

    read_model = ReadModel()

    summary = read_model._build_summary_from_database()

    assert db_session.queried_anomaly_flags is False
    assert summary["anomaly_counts"] == {
        "high_risk_without_recommendation": 1,
        "high_risk_low_confidence": 2,
        "insufficient_data_prediction": 3,
        "missing_key_profile_fields": 4,
        "elevated_forecast_low_risk": 5,
    }
    anomaly_count_conditions = read_model.count_conditions[1:6]
    assert len(anomaly_count_conditions) == len(KNOWN_ANOMALY_TYPES)
    assert all(len(conditions) == 1 for conditions in anomaly_count_conditions)
    assert all(
        "json_contains" in str(conditions[0]).lower()
        for conditions in anomaly_count_conditions
    )
    assert summary["insufficient_data_predictions"] == 3
    assert summary["prophet_model_reuse_count"] == 2
    assert summary["prophet_model_retrain_count"] == 3


class RecordingSummarySession:
    def __init__(self):
        self.queried_anomaly_flags = False

    def query(self, *columns):
        if columns == (PredictionRecord.anomaly_flags,):
            self.queried_anomaly_flags = True
            raise AssertionError("summary should not scan anomaly_flags JSON")
        return RecordingSummaryQuery(columns)


class RecordingSummaryQuery:
    def __init__(self, columns):
        self.columns = columns

    def group_by(self, *columns):
        self.group_by_columns = columns
        return self

    def all(self):
        first_column = self.columns[0]
        if first_column is PredictionRecord.risk_level:
            return [("高风险", 2), ("低风险", 3)]
        if first_column is PredictionRecord.confidence_level:
            return [("low", 1), ("high", 4)]
        return []
