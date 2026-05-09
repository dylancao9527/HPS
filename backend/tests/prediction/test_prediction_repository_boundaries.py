from datetime import datetime
from types import SimpleNamespace

from prediction.infrastructure import prediction_record_repository
from prediction.infrastructure.prediction_payload_assembler import PredictionPayloadAssembler
from prediction.infrastructure.prediction_governance_repository import (
    PredictionGovernanceRepository,
)
from prediction.infrastructure.prediction_governance_read_model import (
    GovernanceQuery,
    PredictionGovernanceReadModel,
)
from prediction.infrastructure.prediction_record_repository import PredictionRecordRepository
from prediction.infrastructure.repositories import PredictionRepository


def test_high_risk_normalization_matches_current_values():
    assert PredictionRepository._is_high_risk("高风险") is True
    assert PredictionRepository._is_high_risk(" high ") is True
    assert PredictionRepository._is_high_risk("HIGH") is True
    assert PredictionRepository._is_high_risk("中风险") is False
    assert PredictionRepository._is_high_risk(None) is False


def test_build_anomaly_flags_marks_high_risk_without_recommendation():
    assert PredictionRepository._build_anomaly_flags(
        {"risk_level": "高风险", "recommendations": []}
    ) == ["high_risk_without_recommendation"]
    assert PredictionRepository._build_anomaly_flags(
        {"risk_level": "高风险", "recommendations": [{"content": "建议"}]}
    ) == []
    assert PredictionRepository._build_anomaly_flags(
        {"risk_level": "中风险", "recommendations": []}
    ) == []


def test_build_governance_list_row_keeps_current_projection():
    row = PredictionRepository._build_governance_list_row(
        {
            "prediction_id": 901,
            "risk_level": "中风险",
            "risk_probability": 0.4567,
            "confidence_level": "medium",
            "data_days_used": 8,
            "input_data": {"age": 56},
            "anomaly_flags": ["flag"],
            "created_at": "2026-04-25T09:30:00",
            "ignored": "value",
        }
    )

    assert row == {
        "prediction_id": 901,
        "risk_level": "中风险",
        "risk_probability": 0.4567,
        "confidence_level": "medium",
        "data_days_used": 8,
        "input_data": {"age": 56},
        "anomaly_flags": ["flag"],
        "created_at": "2026-04-25T09:30:00",
    }


def test_governance_repository_summary_uses_prediction_chain_metrics():
    repository = PredictionGovernanceRepository(
        payload_assembler=SimpleNamespace(
            assemble_prediction_payload=lambda item, prophet_record=None: item
        )
    )
    repository.read_model.governance_base_query = lambda: SimpleNamespace(
        all=lambda: [
            {
                "risk_level": "高风险",
                "confidence_level": "low",
                "data_days_used": 2,
                "cache_mode": "model_reused",
                "recommendations": [{"summary": "建议"}],
            },
            {
                "risk_level": "低风险",
                "confidence_level": "medium",
                "data_days_used": 8,
                "cache_mode": "fresh_train",
                "bp_forecast": [{"systolic": 145, "diastolic": 92}],
                "recommendations": [{"summary": "建议"}],
            },
        ]
    )

    summary = repository.get_governance_summary()

    assert summary["total_predictions"] == 2
    assert summary["high_risk_predictions"] == 1
    assert summary["low_confidence_predictions"] == 1
    assert summary["anomaly_predictions"] == 2
    assert summary["insufficient_data_predictions"] == 1
    assert summary["prophet_model_reuse_count"] == 1
    assert summary["prophet_model_retrain_count"] == 1
    assert summary["anomaly_counts"]["high_risk_low_confidence"] == 1
    assert summary["anomaly_counts"]["elevated_forecast_low_risk"] == 1


def test_governance_repository_lists_predictions_by_anomaly_type():
    repository = PredictionGovernanceRepository(
        payload_assembler=SimpleNamespace(
            assemble_prediction_payload=lambda item, prophet_record=None: item
        )
    )
    repository.read_model.governance_base_query = lambda: InMemoryGovernanceQuery(
        [
            {
                "prediction_id": 901,
                "risk_level": "高风险",
                "confidence_level": "low",
                "data_days_used": 8,
                "recommendations": [{"summary": "建议"}],
            },
            {
                "prediction_id": 902,
                "risk_level": "低风险",
                "confidence_level": "medium",
                "data_days_used": 8,
                "bp_forecast": [{"systolic": 145, "diastolic": 92}],
                "recommendations": [{"summary": "建议"}],
            },
        ]
    )

    result = repository.list_governance_predictions(
        page=1,
        per_page=20,
        anomaly_type="elevated_forecast_low_risk",
    )

    assert result["total"] == 1
    assert result["records"][0]["prediction_id"] == 902
    assert result["records"][0]["anomaly_flags"] == ["elevated_forecast_low_risk"]


def test_governance_read_model_has_anomaly_means_any_anomaly_flag():
    read_model = PredictionGovernanceReadModel(
        payload_assembler=SimpleNamespace(
            assemble_prediction_payload=lambda item, prophet_record=None: item
        )
    )
    read_model.governance_base_query = lambda: InMemoryGovernanceQuery(
        [
            {
                "prediction_id": 901,
                "risk_level": "高风险",
                "confidence_level": "low",
                "data_days_used": 8,
                "recommendations": [{"summary": "建议"}],
            },
            {
                "prediction_id": 902,
                "risk_level": "低风险",
                "confidence_level": "medium",
                "data_days_used": 8,
                "bp_forecast": [{"systolic": 145, "diastolic": 92}],
                "recommendations": [{"summary": "建议"}],
            },
            {
                "prediction_id": 903,
                "risk_level": "中风险",
                "confidence_level": "medium",
                "data_days_used": 8,
                "recommendations": [{"summary": "建议"}],
            },
        ]
    )

    result = read_model.list_predictions(page=1, per_page=20, has_anomaly=True)

    assert [row["prediction_id"] for row in result["records"]] == [901, 902]
    assert result["records"][0]["anomaly_flags"] == ["high_risk_low_confidence"]
    assert result["records"][1]["anomaly_flags"] == ["elevated_forecast_low_risk"]


def test_governance_query_normalizes_pagination_and_filters():
    query = GovernanceQuery.from_filters(
        page=0,
        per_page=-1,
        risk_level=" 高风险 ",
        confidence_level=" low ",
        has_anomaly=False,
        anomaly_type=" insufficient_data_prediction ",
    )

    assert query.page == 1
    assert query.per_page == 20
    assert query.risk_level == "高风险"
    assert query.confidence_level == "low"
    assert query.has_anomaly is False
    assert query.anomaly_type == "insufficient_data_prediction"
    assert query.needs_anomaly_projection_filter is True


def test_governance_prediction_detail_exposes_forecast_summary():
    repository = PredictionGovernanceRepository(
        payload_assembler=SimpleNamespace(
            assemble_prediction_payload=lambda item, prophet_record=None: item
        )
    )
    repository.read_model.governance_base_query = lambda: InMemoryGovernanceQuery(
        [
            {
                "prediction_id": 901,
                "risk_level": "中风险",
                "risk_probability": 0.4567,
                "confidence_level": "medium",
                "data_days_used": 8,
                "bp_forecast": [
                    {"systolic": 132, "diastolic": 84},
                    {"systolic": 142, "diastolic": 91},
                ],
                "recommendations": [{"summary": "建议"}],
                "created_at": "2026-04-25T09:30:00",
            },
        ]
    )

    detail = repository.get_governance_prediction_detail(901)

    assert detail["risk_probability"] == 0.4567
    assert detail["data_days_used"] == 8
    assert detail["forecast_summary"] == {
        "forecast_days": 2,
        "avg_sys": 137.0,
        "avg_dia": 87.5,
        "max_sys": 142.0,
        "max_dia": 91.0,
        "high_bp_days": 1,
        "elevated_bp_days": 2,
        "high_bp_ratio": 0.5,
        "elevated_bp_ratio": 1.0,
        "sys_slope": 10.0,
        "dia_slope": 7.0,
        "sys_volatility": 5.0,
        "dia_volatility": 3.5,
    }


class FakeMapper:
    def assemble_training_meta(self, prophet_record, item):
        return {
            "seasonality": {"weekly_enabled": True},
            "confidence_level": "medium",
            "confidence_reasons": ["short_history"],
        }

    def assemble_input_data(self, item, prophet_record=None):
        return {"age": 56, "_prophet_cache_key": prophet_record.cache_key}

    def assemble_fusion_meta(self, item, prophet_record=None):
        return {"raw_probability": 0.3, "fused_probability": 0.34}

    def assemble_forecast(self, prophet_record, item):
        return [{"day": 1, "systolic": 132, "diastolic": 84}]

    def assemble_recommendations(self, item):
        return {"summary": "保持观察"}


def test_assemble_prediction_payload_uses_mapper_projection():
    repository = PredictionRepository()
    repository.mapper = FakeMapper()
    created_at = datetime(2026, 4, 25, 9, 30, 0)
    item = SimpleNamespace(
        id=901,
        prophet_prediction_id=902,
        prophet_prediction=None,
        created_at=created_at,
        to_dict=lambda: {
            "id": 901,
            "user_id": 42,
            "risk_probability": 0.34,
            "risk_level": "中风险",
            "prophet_prediction_id": 902,
            "created_at": created_at.isoformat(),
        },
    )
    prophet_record = SimpleNamespace(
        id=902,
        forecast_days=7,
        data_days_used=8,
        total_history_days=12,
        history_window_capped=False,
        data_range="2026-04-01 ~ 2026-04-08",
        cache_key="cache-key",
    )

    row = repository.assemble_prediction_payload(item, prophet_record=prophet_record)

    assert row["prediction_id"] == 901
    assert row["created_at"] == created_at.isoformat()
    assert row["input_data"] == {"age": 56, "_prophet_cache_key": "cache-key"}
    assert row["bp_forecast"] == [{"day": 1, "systolic": 132, "diastolic": 84}]
    assert row["recommendations"] == {"summary": "保持观察"}
    assert row["seasonality"] == {"weekly_enabled": True}
    assert row["confidence_level"] == "medium"
    assert row["cache_mode"] == "fresh_train"
    assert "from_cache" not in row
    assert row["forecast_days"] == 7


def test_payload_assembler_reads_legacy_prediction_recommendation_payload():
    created_at = datetime(2026, 4, 25, 9, 30, 0)
    item = SimpleNamespace(
        id=901,
        prophet_prediction_id=902,
        prophet_prediction=None,
        created_at=created_at,
        input_snapshot=None,
        fusion_meta=None,
        confidence_reasons=[],
        recommendation_items=[
            SimpleNamespace(category="guideline_payload", title="summary", content="摘要"),
            SimpleNamespace(category="guideline_payload", title="reason", content="原因"),
            SimpleNamespace(category="guideline_payload", title="action", content="行动一"),
            SimpleNamespace(category="guideline_payload", title="source_label", content="来源"),
        ],
        to_dict=lambda: {
            "id": 901,
            "user_id": 42,
            "risk_probability": 0.34,
            "risk_level": "中风险",
            "prophet_prediction_id": 902,
            "created_at": created_at.isoformat(),
        },
    )
    prophet_record = SimpleNamespace(
        id=902,
        forecast_days=7,
        data_days_used=8,
        total_history_days=12,
        history_window_capped=False,
        data_range="2026-04-01 ~ 2026-04-08",
        cache_key="cache-key",
        forecast_points=[],
        training_meta_row=None,
    )

    row = PredictionPayloadAssembler().assemble_prediction_payload(
        item,
        prophet_record=prophet_record,
    )

    assert row["input_data"] == {}
    assert row["fusion_meta"] == {"reasons": []}
    assert row["training_meta"] == {"confidence_reasons": []}
    assert row["recommendations"] == [
        {
            "topic": "follow_up",
            "summary": "摘要",
            "reason": "原因",
            "actions": ["行动一"],
            "source_label": "来源",
        }
    ]


def test_payload_assembler_recovers_model_reuse_cache_mode():
    class ReuseMapper(FakeMapper):
        def assemble_training_meta(self, prophet_record, item):
            return {
                "confidence_level": "medium",
                "confidence_reasons": [],
                "model_strategy": "reuse_existing_model",
            }

    created_at = datetime(2026, 4, 25, 9, 30, 0)
    item = SimpleNamespace(
        id=901,
        prophet_prediction_id=902,
        prophet_prediction=None,
        created_at=created_at,
        to_dict=lambda: {
            "id": 901,
            "user_id": 42,
            "risk_probability": 0.34,
            "risk_level": "中风险",
            "prophet_prediction_id": 902,
            "created_at": created_at.isoformat(),
        },
    )
    prophet_record = SimpleNamespace(
        id=902,
        forecast_days=7,
        data_days_used=8,
        total_history_days=12,
        history_window_capped=False,
        data_range="2026-04-01 ~ 2026-04-08",
        cache_key="cache-key",
    )

    row = PredictionPayloadAssembler(mapper=ReuseMapper()).assemble_prediction_payload(
        item,
        prophet_record=prophet_record,
    )

    assert row["cache_mode"] == "model_reuse"


def test_get_user_uses_session_get(monkeypatch):
    bp_data = RecordingComponent(get_user_result="user-row")

    result = PredictionRepository(bp_data=bp_data).get_user(42)

    assert result == "user-row"
    assert bp_data.calls == [("get_user", (42,), {})]


def test_get_latest_bp_record_delegates_to_bp_data():
    bp_data = RecordingComponent(get_latest_bp_record_result="latest-bp-record")

    result = PredictionRepository(bp_data=bp_data).get_latest_bp_record(42)

    assert result == "latest-bp-record"
    assert bp_data.calls == [("get_latest_bp_record", (42,), {})]


def test_get_active_prophet_model_delegates_to_prophet_models():
    prophet_models = RecordingComponent(get_active_prophet_model_result="active-model")

    result = PredictionRepository(prophet_models=prophet_models).get_active_prophet_model(
        42,
        7,
    )

    assert result == "active-model"
    assert prophet_models.calls == [("get_active_prophet_model", (42, 7), {})]


def test_prediction_repository_does_not_expose_reusable_prediction_lookup():
    assert not hasattr(PredictionRepository(), "get_reusable_prediction")


class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.committed = True


class InMemoryGovernanceQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args):
        return self

    def outerjoin(self, *args):
        return self

    def all(self):
        return self.items

    def paginate(self, *, page, per_page, error_out):
        start = (page - 1) * per_page
        end = start + per_page
        return SimpleNamespace(
            items=self.items[start:end],
            total=len(self.items),
            pages=1 if self.items else 0,
        )

    def first(self):
        return self.items[0] if self.items else None


class CompactRowsMapper:
    def __init__(self):
        self.payloads = []
        self.rows = SimpleNamespace(
            prophet_prediction=SimpleNamespace(id=902),
            prediction_record=SimpleNamespace(id=901),
        )

    def build_compact_prediction(self, payload):
        self.payloads.append(payload)
        return self.rows


class LegacyOnlyRowsMapper:
    def build_normalized_prediction(self, payload):
        raise AssertionError("legacy normalized mapper should no longer be used")


def test_record_repository_save_prediction_uses_compact_rows_boundary(monkeypatch):
    mapper = CompactRowsMapper()
    fake_session = FakeSession()
    monkeypatch.setattr(
        prediction_record_repository.db,
        "session",
        fake_session,
        raising=False,
    )
    repository = PredictionRecordRepository(
        payload_assembler=SimpleNamespace(),
        mapper=mapper,
    )
    payload = {"user_id": 42, "risk_probability": 0.42}

    record, prophet_record = repository.save_prediction(payload)

    assert mapper.payloads == [payload]
    assert fake_session.added == [mapper.rows.prediction_record]
    assert fake_session.committed is True
    assert record is mapper.rows.prediction_record
    assert prophet_record is mapper.rows.prophet_prediction


def test_record_repository_save_prediction_requires_compact_write_mapper(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(
        prediction_record_repository.db,
        "session",
        fake_session,
        raising=False,
    )
    repository = PredictionRecordRepository(
        payload_assembler=SimpleNamespace(),
        mapper=LegacyOnlyRowsMapper(),
    )

    try:
        repository.save_prediction({"user_id": 42, "risk_probability": 0.42})
    except AttributeError:
        pass
    else:
        raise AssertionError("save_prediction should require build_compact_prediction")


class TrendProjectionQuery:
    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    def filter(self, *args):
        self.calls.append(("filter", args))
        return self

    def order_by(self, *args):
        self.calls.append(("order_by", args))
        return self

    def limit(self, value):
        self.calls.append(("limit", value))
        return self

    def all(self):
        self.calls.append(("all", ()))
        return self.rows


class TrendProjectionSession:
    def __init__(self, rows):
        self.query_args = None
        self.query_builder = TrendProjectionQuery(rows)

    def query(self, *args):
        self.query_args = args
        return self.query_builder


def test_record_repository_lists_prediction_trend_without_payload_assembler(
    monkeypatch,
):
    created_at = datetime(2026, 4, 25, 9, 30, 0)
    session = TrendProjectionSession(
        [
            SimpleNamespace(
                id=11,
                created_at=created_at,
                risk_probability=0.42,
                risk_level="中风险",
            )
        ]
    )
    monkeypatch.setattr(
        prediction_record_repository.db,
        "session",
        session,
        raising=False,
    )
    repository = PredictionRecordRepository(
        payload_assembler=SimpleNamespace(
            assemble_prediction_payload=lambda item: (_ for _ in ()).throw(
                AssertionError("prediction trend should not assemble full payload")
            )
        )
    )

    result = repository.list_prediction_trend(user_id=42, limit=5)

    assert [column.key for column in session.query_args] == [
        "id",
        "created_at",
        "risk_probability",
        "risk_level",
    ]
    assert [name for name, _ in session.query_builder.calls] == [
        "filter",
        "order_by",
        "limit",
        "all",
    ]
    assert session.query_builder.calls[2] == ("limit", 5)
    assert result == [
        {
            "id": 11,
            "created_at": created_at.isoformat(),
            "risk_probability": 0.42,
            "risk_level": "中风险",
        }
    ]


def test_get_prediction_history_delegates_to_records():
    records = RecordingComponent(
        get_prediction_history_result={
            "records": [{"prediction_id": "row-1"}],
            "total": 1,
            "page": 2,
            "pages": 1,
        }
    )

    result = PredictionRepository(records=records).get_prediction_history(
        user_id=42,
        page=2,
        per_page=5,
    )

    assert result == {
        "records": [{"prediction_id": "row-1"}],
        "total": 1,
        "page": 2,
        "pages": 1,
    }
    assert records.calls == [
        (
            "get_prediction_history",
            (),
            {
                "user_id": 42,
                "page": 2,
                "per_page": 5,
                "start_date": "",
                "end_date": "",
            },
        )
    ]


def test_get_bp_data_status_delegates_to_bp_data():
    bp_data = RecordingComponent(
        get_bp_data_status_result={
            "total_records": 4,
            "total_days": 3,
            "forecast_days": 7,
            "minimum_days": 3,
            "recommended_days_min": 21,
            "recommended_days_max": 35,
            "recommended_records_min": 63,
            "recommended_records_max": 105,
            "meets_minimum": True,
            "meets_recommended": False,
            "status": "warning",
        }
    )

    result = PredictionRepository(bp_data=bp_data).get_bp_data_status(
        user_id=42,
        forecast_days=7,
    )

    assert result == {
        "total_records": 4,
        "total_days": 3,
        "forecast_days": 7,
        "minimum_days": 3,
        "recommended_days_min": 21,
        "recommended_days_max": 35,
        "recommended_records_min": 63,
        "recommended_records_max": 105,
        "meets_minimum": True,
        "meets_recommended": False,
        "status": "warning",
    }
    assert bp_data.calls == [
        ("get_bp_data_status", (), {"user_id": 42, "forecast_days": 7})
    ]


class RecordingComponent:
    def __init__(self, **results):
        self.results = results
        self.calls = []

    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return self.results.get(f"{name}_result")

        return method
