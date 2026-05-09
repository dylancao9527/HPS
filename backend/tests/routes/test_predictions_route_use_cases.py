from flask import Flask

from prediction.application.batch_delete_predictions import BatchDeletePredictionsUseCase
from prediction.application.composition import PredictionUseCaseFactory
from prediction.application.delete_prediction import DeletePredictionUseCase
from prediction.application.get_bp_data_status import GetBPDataStatusUseCase
from prediction.application.get_prediction_history import GetPredictionHistoryUseCase
from prediction.application.list_prediction_trend import ListPredictionTrendUseCase
from prediction.application.predict_use_case import PredictUseCase
from prediction.application.user_prediction_records import UserPredictionRecordActions
from prediction.domain.bp_data_policy import InsufficientBPDataForPredictionError
from prediction.schemas.commands import DeletePredictionCommand, GetPredictionHistoryQuery
from prediction.schemas.input_snapshot import IncompleteRiskFactorProfileError
from routes import predictions


def _app():
    return Flask(__name__)


def _json_and_status(result):
    if isinstance(result, tuple):
        response, status = result
    else:
        response, status = result, 200
    return response.get_json(), status


class FakeUseCase:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class UnexpectedUseCase:
    def execute(self, *args, **kwargs):
        raise AssertionError("unsupported forecast period should not reach use case")


class FakeUseCaseFactory:
    def __init__(self):
        self.calls = []

    def _record(self, name):
        self.calls.append(name)
        return name

    def build_predict_use_case(self):
        return self._record("predict")

    def build_prediction_history_use_case(self):
        return self._record("history")

    def build_delete_prediction_use_case(self):
        return self._record("delete")

    def build_bp_data_status_use_case(self):
        return self._record("bp-status")

    def build_batch_delete_predictions_use_case(self):
        return self._record("batch-delete")

    def build_user_prediction_record_actions(self):
        return self._record("record-actions")


def test_prediction_route_builders_delegate_to_composition_factory(monkeypatch):
    factory = FakeUseCaseFactory()
    monkeypatch.setattr(predictions, "prediction_use_cases", factory)

    assert predictions.build_predict_use_case() == "predict"
    assert predictions.build_prediction_history_use_case() == "history"
    assert predictions.build_delete_prediction_use_case() == "delete"
    assert predictions.build_bp_data_status_use_case() == "bp-status"
    assert predictions.build_batch_delete_predictions_use_case() == "batch-delete"
    assert predictions.build_user_prediction_record_actions() == "record-actions"
    assert factory.calls == [
        "predict",
        "history",
        "delete",
        "bp-status",
        "batch-delete",
        "record-actions",
    ]


def test_predictions_route_no_longer_exposes_profile_trend_helpers():
    assert not hasattr(predictions, "build_list_prophet_predictions_use_case")
    assert not hasattr(predictions, "build_delete_prophet_prediction_use_case")
    assert not hasattr(predictions, "get_prophet_predictions")
    assert not hasattr(predictions, "delete_prophet_prediction")


def test_predict_route_rejects_non_7_day_forecast_period(monkeypatch, fake_user):
    app = _app()
    monkeypatch.setattr(
        predictions,
        "build_predict_use_case",
        lambda: UnexpectedUseCase(),
    )

    with app.test_request_context(json={"forecast_days": 14}):
        payload, status = _json_and_status(predictions.predict.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "预测周期已统一为未来7天"}


def test_predict_route_rejects_missing_risk_factor_profile(monkeypatch, fake_user):
    app = _app()

    class MissingRiskProfileUseCase:
        def execute(self, command):
            raise IncompleteRiskFactorProfileError("请先完善风险因素档案")

    monkeypatch.setattr(
        predictions,
        "build_predict_use_case",
        lambda: MissingRiskProfileUseCase(),
    )

    with app.test_request_context(json={}):
        payload, status = _json_and_status(predictions.predict.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "请先完善风险因素档案"}


def test_predict_route_rejects_insufficient_bp_days(monkeypatch, fake_user):
    app = _app()

    class InsufficientBPDataUseCase:
        def execute(self, command):
            raise InsufficientBPDataForPredictionError(
                "血压记录不足：请至少记录 3 个自然日后再进行预测"
            )

    monkeypatch.setattr(
        predictions,
        "build_predict_use_case",
        lambda: InsufficientBPDataUseCase(),
    )

    with app.test_request_context(json={}):
        payload, status = _json_and_status(predictions.predict.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "血压记录不足：请至少记录 3 个自然日后再进行预测"}


def test_bp_data_status_route_rejects_non_7_day_forecast_period(
    monkeypatch,
    fake_user,
):
    app = _app()
    monkeypatch.setattr(
        predictions,
        "build_bp_data_status_use_case",
        lambda: UnexpectedUseCase(),
    )

    with app.test_request_context("/api/bp-data-status?forecast_days=3"):
        payload, status = _json_and_status(
            predictions.bp_data_status.__wrapped__(fake_user)
        )

    assert status == 400
    assert payload == {"error": "预测周期已统一为未来7天"}


def test_batch_delete_predictions_without_ids_returns_400(monkeypatch, fake_user):
    app = _app()
    use_case = FakeUseCase(({"error": "请选择要删除的记录"}, 400))
    monkeypatch.setattr(
        predictions,
        "build_batch_delete_predictions_use_case",
        lambda: use_case,
    )

    with app.test_request_context(json={"ids": []}):
        payload, status = _json_and_status(
            predictions.batch_delete_predictions.__wrapped__(fake_user)
        )

    assert status == 400
    assert payload == {"error": "请选择要删除的记录"}
    assert use_case.calls == [{"user_id": 42, "prediction_ids": []}]


def test_batch_delete_predictions_deletes_matching_rows(monkeypatch, fake_user):
    app = _app()
    use_case = FakeUseCase({"message": "已删除 2 条记录"})
    monkeypatch.setattr(
        predictions,
        "build_batch_delete_predictions_use_case",
        lambda: use_case,
    )

    with app.test_request_context(json={"ids": [1, 2]}):
        payload, status = _json_and_status(
            predictions.batch_delete_predictions.__wrapped__(fake_user)
        )

    assert status == 200
    assert payload == {"message": "已删除 2 条记录"}
    assert use_case.calls == [{"user_id": 42, "prediction_ids": [1, 2]}]


class FakeRouteRepository:
    def __init__(self):
        self.calls = []
        self.history_result = None

    def get_prediction_history(self, **kwargs):
        self.calls.append(("get_prediction_history", kwargs))
        return self.history_result

    def delete_prediction(self, **kwargs):
        self.calls.append(("delete_prediction", kwargs))
        return False

    def batch_delete_predictions(self, **kwargs):
        self.calls.append(("batch_delete_predictions", kwargs))
        return 2

    def list_prediction_trend(self, **kwargs):
        self.calls.append(("list_prediction_trend", kwargs))
        return [
            {
                "id": 11,
                "created_at": "2026-04-25T09:30:00",
                "risk_probability": 0.42,
                "risk_level": "中风险",
            }
        ]


class FakeCompositionRepository:
    def __init__(self):
        self.records = FakeRouteRepository()


def test_prediction_use_case_factory_centralizes_use_case_assembly():
    repository = FakeCompositionRepository()
    prophet_gateway = object()
    risk_gateway = object()
    recommendation_service = object()
    risk_level_service = object()

    def now_provider():
        return "now"

    factory = PredictionUseCaseFactory(
        repository_factory=lambda: repository,
        prophet_gateway_factory=lambda: prophet_gateway,
        risk_gateway_factory=lambda: risk_gateway,
        recommendation_service_factory=lambda: recommendation_service,
        risk_level_service_factory=lambda: risk_level_service,
        now_provider=now_provider,
    )

    predict_use_case = factory.build_predict_use_case()
    history_use_case = factory.build_prediction_history_use_case()
    delete_use_case = factory.build_delete_prediction_use_case()
    bp_status_use_case = factory.build_bp_data_status_use_case()
    batch_delete_use_case = factory.build_batch_delete_predictions_use_case()
    prediction_trend_use_case = factory.build_list_prediction_trend_use_case()

    assert isinstance(predict_use_case, PredictUseCase)
    assert predict_use_case.repository is repository
    assert predict_use_case.prophet_gateway is prophet_gateway
    assert predict_use_case.risk_gateway is risk_gateway
    assert predict_use_case.recommendation_service is recommendation_service
    assert predict_use_case.risk_level_service is risk_level_service
    assert predict_use_case.now_provider is now_provider
    assert not hasattr(predict_use_case, "model_reuse_window")
    assert not hasattr(predict_use_case, "result_metadata_window")
    assert isinstance(history_use_case, GetPredictionHistoryUseCase)
    assert isinstance(delete_use_case, DeletePredictionUseCase)
    assert isinstance(bp_status_use_case, GetBPDataStatusUseCase)
    assert isinstance(batch_delete_use_case, BatchDeletePredictionsUseCase)
    assert isinstance(prediction_trend_use_case, ListPredictionTrendUseCase)
    assert history_use_case.actions.repository is repository.records
    assert delete_use_case.actions.repository is repository.records
    assert batch_delete_use_case.actions.repository is repository.records
    assert prediction_trend_use_case.actions.repository is repository.records
    assert bp_status_use_case.repository is repository


def test_batch_delete_use_case_handles_empty_ids():
    repository = FakeRouteRepository()
    result = BatchDeletePredictionsUseCase(repository=repository).execute(
        user_id=42,
        prediction_ids=[],
    )

    assert result == ({"error": "请选择要删除的记录"}, 400)
    assert repository.calls == []


def test_user_prediction_record_actions_centralize_user_record_behaviors():
    repository = FakeRouteRepository()
    repository.history_result = {
        "records": [{"prediction_id": 901}],
        "total": 1,
        "page": 2,
        "pages": 1,
    }
    actions = UserPredictionRecordActions(repository=repository)

    history = actions.get_history(
        GetPredictionHistoryQuery(
            user_id=42,
            page=2,
            per_page=5,
            start_date="2026-04-01",
            end_date="2026-04-30",
        )
    )
    delete_miss = actions.delete_prediction(
        DeletePredictionCommand(user_id=42, prediction_id=99)
    )
    batch_empty = actions.batch_delete_predictions(user_id=42, prediction_ids=[])
    batch_hit = actions.batch_delete_predictions(user_id=42, prediction_ids=[1, 2])
    prediction_trend = actions.list_prediction_trend(user_id=42, limit=5)

    assert history == repository.history_result
    assert delete_miss == ({"error": "记录不存在"}, 404)
    assert batch_empty == ({"error": "请选择要删除的记录"}, 400)
    assert batch_hit == {"message": "已删除 2 条记录"}
    assert prediction_trend == {
        "records": [
            {
                "id": 11,
                "created_at": "2026-04-25T09:30:00",
                "risk_probability": 0.42,
                "risk_level": "中风险",
            }
        ]
    }
    assert repository.calls == [
        (
            "get_prediction_history",
            {
                "user_id": 42,
                "page": 2,
                "per_page": 5,
                "start_date": "2026-04-01",
                "end_date": "2026-04-30",
            },
        ),
        ("delete_prediction", {"user_id": 42, "prediction_id": 99}),
        (
            "batch_delete_predictions",
            {"user_id": 42, "prediction_ids": [1, 2]},
        ),
        ("list_prediction_trend", {"user_id": 42, "limit": 5}),
    ]


def test_route_use_cases_delegate_to_repository():
    repository = FakeRouteRepository()

    batch_result = BatchDeletePredictionsUseCase(repository=repository).execute(
        user_id=42,
        prediction_ids=[1, 2],
    )
    list_result = ListPredictionTrendUseCase(repository=repository).execute(
        user_id=42,
        limit=5,
    )

    assert batch_result == {"message": "已删除 2 条记录"}
    assert list_result == {
        "records": [
            {
                "id": 11,
                "created_at": "2026-04-25T09:30:00",
                "risk_probability": 0.42,
                "risk_level": "中风险",
            }
        ]
    }
    assert repository.calls == [
        (
            "batch_delete_predictions",
            {"user_id": 42, "prediction_ids": [1, 2]},
        ),
        ("list_prediction_trend", {"user_id": 42, "limit": 5}),
    ]
