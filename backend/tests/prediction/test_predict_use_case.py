from types import SimpleNamespace

from prediction.application.predict_use_case import PredictUseCase
from prediction.application import predict_use_case
from prediction.domain.bp_data_policy import InsufficientBPDataForPredictionError
from prediction.domain.run_key_policy import build_prediction_run_key
from prediction.infrastructure.prophet_gateway import AGGREGATION_MODE
from prediction.schemas.commands import PredictCommand
from prediction.schemas.input_snapshot import (
    IncompleteRiskFactorProfileError,
    LEGACY_CACHE_SNAPSHOT_KEY,
    LEGACY_PROPHET_CACHE_KEY,
    MODEL_STATE_SNAPSHOT_KEY,
    PredictionInputSnapshot,
    PREDICTION_RUN_KEY,
)


class FakeProphetGateway:
    def __init__(self, forecast, training_meta, model_strategy=None):
        self.forecast = forecast
        self.training_meta = training_meta
        self.model_strategy = model_strategy
        self.inspect_calls = []
        self.predict_calls = []

    def inspect(self, user_id, forecast_days):
        self.inspect_calls.append((user_id, forecast_days))
        return {
            "model_version": "user-prophet-v1",
            "data_signature": "sig-001",
            "model_cache_hit": False,
        }

    def predict(self, user_id, forecast_days):
        self.predict_calls.append((user_id, forecast_days))
        result = {
            "forecast": self.forecast,
            "data_days_used": 8,
            "total_history_days": 12,
            "history_window_capped": False,
            "data_range": "2026-04-01 ~ 2026-04-08",
            "training_meta": self.training_meta,
            "seasonality": self.training_meta["seasonality"],
            "model_version": "user-prophet-v1",
            "data_signature": "sig-001",
            "model_cache_hit": False,
        }
        if self.model_strategy:
            result["model_strategy"] = self.model_strategy
        return result


class NoInspectProphetGateway:
    def __init__(self, forecast, training_meta):
        self.forecast = forecast
        self.training_meta = training_meta
        self.predict_calls = []

    def predict(self, user_id, forecast_days):
        self.predict_calls.append((user_id, forecast_days))
        return {
            "forecast": self.forecast,
            "data_days_used": 8,
            "total_history_days": 12,
            "history_window_capped": False,
            "data_range": "2026-04-01 ~ 2026-04-08",
            "training_meta": self.training_meta,
            "seasonality": self.training_meta["seasonality"],
            "model_version": "user-prophet-v1",
            "data_signature": "sig-001",
            "model_cache_hit": False,
        }


class FakeRiskGateway:
    def __init__(self):
        self.calls = []

    def score(self, user_data, forecast):
        self.calls.append((user_data, forecast))
        return 0.31234, {
            "bp_meds_input": user_data["BPMeds"],
            "bp_meds_model_value": 0,
            "bp_meds_policy": "neutralized_for_conservative_inference",
        }


class FakeRecommendationService:
    def __init__(self):
        self.calls = []

    def generate(self, *, guideline_signal, risk_probability):
        self.calls.append((guideline_signal, risk_probability))
        return {
            "summary": "保持观察",
            "reason": "近期血压存在波动",
            "actions": ["继续记录血压"],
            "matched_knowledge_ids": ["kb-1"],
            "source_label": "指南库",
        }


class StrictGuidelineRecommendationService:
    def __init__(self):
        self.calls = []

    def generate(self, *, guideline_signal, risk_probability):
        self.calls.append(
            {
                "guideline_signal": guideline_signal,
                "risk_probability": risk_probability,
            }
        )
        return [
            {
                "topic": "follow_up",
                "summary": "保持观察",
                "reason": "近期血压存在波动",
                "actions": ["继续记录血压"],
                "source_label": "指南库",
            }
        ]


class FakeRiskLevelService:
    def get_level(self, probability):
        if probability >= 0.5:
            return "高风险", "high", "#dc2626"
        return "中风险", "medium", "#d97706"


class FakeRepository:
    def __init__(self, *, user, latest_bp, fixed_now, bp_data_status=None):
        self.user = user
        self.latest_bp = latest_bp
        self.fixed_now = fixed_now
        self.bp_data_status = bp_data_status or {
            "total_records": 9,
            "total_days": 3,
            "forecast_days": 7,
            "minimum_days": 3,
            "meets_minimum": True,
            "meets_recommended": False,
            "status": "warning",
        }
        self.saved_payload = None
        self.saved_payloads = []
        self.bp_status_calls = []

    def get_user(self, user_id):
        return self.user

    def get_latest_bp_record(self, user_id):
        return self.latest_bp

    def get_bp_data_status(self, *, user_id, forecast_days):
        self.bp_status_calls.append((user_id, forecast_days))
        return self.bp_data_status

    def save_prediction(self, payload):
        self.saved_payload = payload
        self.saved_payloads.append(payload)
        prediction_id = 900 + len(self.saved_payloads)
        record = SimpleNamespace(
            id=prediction_id,
            risk_probability=payload["risk_probability"],
            risk_level=payload["risk_level"],
            created_at=self.fixed_now,
        )
        return record, None

    def assemble_prediction_payload(self, record, prophet_record):
        return {
            "prediction_id": record.id,
            "risk_probability": record.risk_probability,
            "risk_level": record.risk_level,
            "bp_forecast": [{"day": 1, "systolic": 132, "diastolic": 84}],
            "forecast_days": 7,
            "data_days_used": 8,
            "total_history_days": 12,
            "history_window_capped": False,
            "data_range": "2026-04-01 ~ 2026-04-08",
            "seasonality": {"weekly_enabled": True},
            "training_meta": {"confidence_level": "medium"},
            "confidence_level": "medium",
            "confidence_reasons": ["short_history"],
            "recommendations": {"summary": "保持观察"},
            "input_data": {"age": 56},
            "fusion_meta": {"raw_probability": 0.3, "fused_probability": 0.34},
            "created_at": record.created_at.isoformat(),
            "prophet_prediction_id": None,
        }


def make_use_case(repository, prophet_gateway, risk_gateway, recommendation_service, fixed_now):
    return PredictUseCase(
        repository=repository,
        prophet_gateway=prophet_gateway,
        risk_gateway=risk_gateway,
        recommendation_service=recommendation_service,
        risk_level_service=FakeRiskLevelService(),
        now_provider=lambda: fixed_now,
    )


def test_prediction_input_snapshot_separates_model_input_from_persistence_metadata(
    fake_user,
    fake_bp_record,
):
    snapshot = PredictionInputSnapshot.from_user_and_latest_bp(
        user=fake_user,
        latest_bp=fake_bp_record,
    )
    model_input = snapshot.to_model_input()
    persistence_payload = snapshot.to_persistence_payload(
        model_state={"model_version": "v1"},
        prediction_run_key="run-key",
    )

    assert model_input == {
        "age": 56,
        "male": 1,
        "BMI": 27.4,
        "currentSmoker": 1,
        "cigsPerDay": 5,
        "BPMeds": 1,
        "diabetes": 0,
        "sysBP": 138,
        "diaBP": 86,
        "heartRate": 72,
        "totChol": 190,
        "glucose": 96,
    }
    assert MODEL_STATE_SNAPSHOT_KEY not in model_input
    assert persistence_payload[MODEL_STATE_SNAPSHOT_KEY] == {"model_version": "v1"}
    assert persistence_payload[PREDICTION_RUN_KEY] == "run-key"
    assert LEGACY_CACHE_SNAPSHOT_KEY not in persistence_payload
    assert LEGACY_PROPHET_CACHE_KEY not in persistence_payload


def test_prediction_input_snapshot_requires_complete_risk_factor_profile(
    fake_bp_record,
):
    missing_profile_user = SimpleNamespace(id=42, risk_factor_profile=None)
    incomplete_profile_user = SimpleNamespace(
        id=42,
        risk_factor_profile=SimpleNamespace(profile_complete=False),
    )

    for user in (missing_profile_user, incomplete_profile_user):
        try:
            PredictionInputSnapshot.from_user_and_latest_bp(
                user=user,
                latest_bp=fake_bp_record,
            )
        except IncompleteRiskFactorProfileError as exc:
            assert str(exc) == "请先完善风险因素档案"
        else:
            raise AssertionError("missing or incomplete risk factor profile should block prediction")


def test_execute_allows_optional_risk_factor_inputs_to_remain_missing(
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    user = SimpleNamespace(
        id=42,
        risk_factor_profile=SimpleNamespace(
            age=58,
            male=1,
            bmi=25.1,
            current_smoker=None,
            cigs_per_day=None,
            bp_meds=None,
            diabetes=None,
            tot_chol=None,
            glucose=None,
            profile_complete=True,
        ),
    )
    repository = FakeRepository(user=user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    risk_gateway = FakeRiskGateway()
    use_case = make_use_case(
        repository,
        FakeProphetGateway(sample_forecast, sample_training_meta),
        risk_gateway,
        FakeRecommendationService(),
        fixed_now,
    )

    result = use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    assert result.prediction_id == 901
    assert risk_gateway.calls[0][0]["currentSmoker"] is None
    assert risk_gateway.calls[0][0]["BPMeds"] is None
    assert risk_gateway.calls[0][0]["diabetes"] is None
    assert repository.saved_payload["input_data"]["totChol"] is None
    assert len(repository.saved_payloads) == 1


def test_execute_uses_latest_bp_and_persists_prediction(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    prophet_gateway = FakeProphetGateway(sample_forecast, sample_training_meta)
    risk_gateway = FakeRiskGateway()
    recommendation_service = FakeRecommendationService()
    use_case = make_use_case(
        repository,
        prophet_gateway,
        risk_gateway,
        recommendation_service,
        fixed_now,
    )

    result = use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    assert prophet_gateway.inspect_calls == []
    assert prophet_gateway.predict_calls[0][0:2] == (42, 7)
    assert repository.saved_payload["input_data"]["sysBP"] == 138
    assert repository.saved_payload["input_data"]["diaBP"] == 86
    assert repository.saved_payload["forecast_days"] == 7
    assert result.prediction_id == 901
    assert result.prophet_prediction_id is None
    assert result.cache_mode == "fresh_train"
    assert result.created_at == fixed_now.isoformat()
    for legacy_result_cache_field in (
        "from_cache",
        "cached_at",
        "cache_expires_at",
        "result_cache_hours",
        "reuse_window_minutes",
    ):
        assert not hasattr(result, legacy_result_cache_field)


def test_execute_blocks_when_bp_days_are_below_minimum(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(
        user=fake_user,
        latest_bp=fake_bp_record,
        fixed_now=fixed_now,
        bp_data_status={
            "total_records": 2,
            "total_days": 2,
            "forecast_days": 7,
            "minimum_days": 3,
            "meets_minimum": False,
            "meets_recommended": False,
            "status": "insufficient",
        },
    )
    prophet_gateway = FakeProphetGateway(sample_forecast, sample_training_meta)
    risk_gateway = FakeRiskGateway()
    use_case = make_use_case(
        repository,
        prophet_gateway,
        risk_gateway,
        FakeRecommendationService(),
        fixed_now,
    )

    try:
        use_case.execute(PredictCommand(user_id=42, forecast_days=7))
    except InsufficientBPDataForPredictionError as exc:
        assert str(exc) == "血压记录不足：请至少记录 3 个自然日后再进行预测"
    else:
        raise AssertionError("insufficient BP natural days should block prediction")

    assert prophet_gateway.predict_calls == []
    assert risk_gateway.calls == []
    assert repository.saved_payloads == []


def test_execute_does_not_record_failed_attempt_when_risk_profile_is_incomplete(
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    user = SimpleNamespace(id=42, risk_factor_profile=None)
    repository = FakeRepository(user=user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    prophet_gateway = FakeProphetGateway(sample_forecast, sample_training_meta)
    risk_gateway = FakeRiskGateway()
    use_case = make_use_case(
        repository,
        prophet_gateway,
        risk_gateway,
        FakeRecommendationService(),
        fixed_now,
    )

    try:
        use_case.execute(PredictCommand(user_id=42, forecast_days=7))
    except IncompleteRiskFactorProfileError:
        pass
    else:
        raise AssertionError("incomplete risk factor profile should block prediction")

    assert repository.bp_status_calls == []
    assert prophet_gateway.predict_calls == []
    assert risk_gateway.calls == []
    assert repository.saved_payloads == []


def test_execute_delegates_to_prediction_run_without_changing_public_interface(
    monkeypatch,
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    constructed = []

    class RecordingPredictionRun:
        def __init__(self, **dependencies):
            self.dependencies = dependencies
            constructed.append(self)

        def execute(self, command):
            self.command = command
            return "prediction-result"

    monkeypatch.setattr(predict_use_case, "PredictionRun", RecordingPredictionRun)
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    prophet_gateway = FakeProphetGateway(sample_forecast, sample_training_meta)
    risk_gateway = FakeRiskGateway()
    recommendation_service = FakeRecommendationService()
    use_case = make_use_case(
        repository,
        prophet_gateway,
        risk_gateway,
        recommendation_service,
        fixed_now,
    )
    command = PredictCommand(user_id=42, forecast_days=7)

    result = use_case.execute(command)

    assert result == "prediction-result"
    assert constructed[0].command is command
    assert constructed[0].dependencies["repository"] is repository
    assert constructed[0].dependencies["prophet_gateway"] is prophet_gateway
    assert constructed[0].dependencies["risk_gateway"] is risk_gateway
    assert constructed[0].dependencies["recommendation_service"] is recommendation_service


def test_execute_uses_default_bp_when_latest_record_missing(
    fake_user,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=None, fixed_now=fixed_now)
    prophet_gateway = FakeProphetGateway(sample_forecast, sample_training_meta)
    risk_gateway = FakeRiskGateway()
    recommendation_service = FakeRecommendationService()
    use_case = make_use_case(
        repository,
        prophet_gateway,
        risk_gateway,
        recommendation_service,
        fixed_now,
    )

    use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    assert repository.saved_payload["input_data"]["sysBP"] == 120
    assert repository.saved_payload["input_data"]["diaBP"] == 80
    assert repository.saved_payload["input_data"]["heartRate"] is None


def test_execute_requests_bp_trend_without_external_inspect_sequence(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    prophet_gateway = NoInspectProphetGateway(sample_forecast, sample_training_meta)
    use_case = make_use_case(
        repository,
        prophet_gateway,
        FakeRiskGateway(),
        FakeRecommendationService(),
        fixed_now,
    )

    result = use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    assert prophet_gateway.predict_calls == [(42, 7)]
    assert result.prediction_id == 901
    assert repository.saved_payload["input_data"][MODEL_STATE_SNAPSHOT_KEY] == {
        "model_version": "user-prophet-v1",
        "data_signature": "sig-001",
        "model_cache_hit": False,
    }
    assert LEGACY_CACHE_SNAPSHOT_KEY not in repository.saved_payload["input_data"]


def test_execute_passes_guideline_signal_explicitly_without_hiding_it_in_input_data(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    recommendation_service = StrictGuidelineRecommendationService()
    use_case = make_use_case(
        repository,
        FakeProphetGateway(sample_forecast, sample_training_meta),
        FakeRiskGateway(),
        recommendation_service,
        fixed_now,
    )

    use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    assert len(recommendation_service.calls) == 1
    assert recommendation_service.calls[0]["guideline_signal"] == {
        "risk_level": "medium",
        "high_bp_days": 1,
        "trend_direction": "upward",
        "record_days": 8,
        "confidence_level": "medium",
        "bp_grade": "normal_high",
    }
    assert "_guideline_signal" not in repository.saved_payload["input_data"]


def test_execute_can_disable_trend_fusion_and_persist_raw_risk_probability(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    use_case = make_use_case(
        repository,
        FakeProphetGateway(sample_forecast, sample_training_meta),
        FakeRiskGateway(),
        FakeRecommendationService(),
        fixed_now,
    )

    result = use_case.execute(
        PredictCommand(user_id=42, forecast_days=7, use_trend_fusion=False)
    )

    assert result.risk_probability == 0.3123
    assert repository.saved_payload["risk_probability"] == 0.3123
    assert repository.saved_payload["fusion_meta"]["fused_probability"] == 0.31234
    assert repository.saved_payload["fusion_meta"]["trend_adjustment"] == 0.0
    assert repository.saved_payload["fusion_meta"]["medication_adjustment"] == 0.0


def test_prediction_run_persists_traceable_prediction_payload(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    risk_gateway = FakeRiskGateway()
    recommendation_service = StrictGuidelineRecommendationService()
    use_case = make_use_case(
        repository,
        FakeProphetGateway(sample_forecast, sample_training_meta),
        risk_gateway,
        recommendation_service,
        fixed_now,
    )

    result = use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    saved = repository.saved_payload
    assert risk_gateway.calls[0][0]["age"] == 56
    assert MODEL_STATE_SNAPSHOT_KEY not in risk_gateway.calls[0][0]
    assert LEGACY_CACHE_SNAPSHOT_KEY not in risk_gateway.calls[0][0]
    assert LEGACY_PROPHET_CACHE_KEY not in risk_gateway.calls[0][0]
    assert risk_gateway.calls[0][1] == sample_forecast
    assert saved["input_data"]["sysBP"] == 138
    assert saved["input_data"][PREDICTION_RUN_KEY] == saved["cache_key"]
    assert LEGACY_CACHE_SNAPSHOT_KEY not in saved["input_data"]
    assert LEGACY_PROPHET_CACHE_KEY not in saved["input_data"]
    assert saved["bp_forecast"] == sample_forecast
    assert saved["fusion_meta"]["raw_probability"] == 0.3123
    assert saved["recommendations"] == result.recommendations
    assert recommendation_service.calls[0]["guideline_signal"]["risk_level"] == "medium"
    assert result.risk_level == "中风险"
    assert result.risk_level_en == "medium"


def test_execute_reuses_prophet_model_without_replaying_cached_prediction(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    repository = FakeRepository(user=fake_user, latest_bp=fake_bp_record, fixed_now=fixed_now)
    prophet_gateway = FakeProphetGateway(
        sample_forecast,
        sample_training_meta,
        model_strategy="reuse_existing_model",
    )
    use_case = make_use_case(
        repository,
        prophet_gateway,
        FakeRiskGateway(),
        FakeRecommendationService(),
        fixed_now,
    )

    first = use_case.execute(PredictCommand(user_id=42, forecast_days=7))
    second = use_case.execute(PredictCommand(user_id=42, forecast_days=7))

    assert len(repository.saved_payloads) == 2
    assert [call[:2] for call in prophet_gateway.predict_calls] == [(42, 7), (42, 7)]
    assert first.prediction_id != second.prediction_id
    assert second.cache_mode == "model_reuse"
    for legacy_result_cache_field in (
        "from_cache",
        "cached_at",
        "cache_expires_at",
        "result_cache_hours",
        "reuse_window_minutes",
    ):
        assert not hasattr(second, legacy_result_cache_field)


def test_prediction_run_key_is_stable_and_input_sensitive(
    fake_user,
    fake_bp_record,
    fixed_now,
    sample_forecast,
    sample_training_meta,
):
    user_data = {
        "age": 56,
        "male": 1,
        "BMI": 27.4,
        "currentSmoker": 1,
        "cigsPerDay": 5,
        "BPMeds": 1,
        "diabetes": 0,
        "sysBP": 138,
        "diaBP": 86,
        "heartRate": 72,
        "totChol": 190,
        "glucose": 96,
    }

    key = build_prediction_run_key(
        user_id=42,
        forecast_days=7,
        model_version="v1",
        data_signature="sig",
        aggregation_mode=AGGREGATION_MODE,
        risk_inputs=user_data,
    )
    same_key = build_prediction_run_key(
        user_id=42,
        forecast_days=7,
        model_version="v1",
        data_signature="sig",
        aggregation_mode=AGGREGATION_MODE,
        risk_inputs=dict(reversed(list(user_data.items()))),
    )
    changed_key = build_prediction_run_key(
        user_id=42,
        forecast_days=14,
        model_version="v1",
        data_signature="sig",
        aggregation_mode=AGGREGATION_MODE,
        risk_inputs=user_data,
    )

    assert key == same_key
    assert key != changed_key
    assert len(key) == 64


def test_predict_use_case_does_not_expose_cached_record_replay_builder(fixed_now):
    repository = FakeRepository(user=None, latest_bp=None, fixed_now=fixed_now)
    use_case = make_use_case(
        repository,
        prophet_gateway=SimpleNamespace(),
        risk_gateway=SimpleNamespace(),
        recommendation_service=SimpleNamespace(),
        fixed_now=fixed_now,
    )

    assert not hasattr(use_case, "_result_from_records")
