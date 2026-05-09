from flask import Flask

from routes import profile
from services import profile_service


def _app():
    return Flask(__name__)


def _json_and_status(result):
    if isinstance(result, tuple):
        response, status = result
    else:
        response, status = result, 200
    return response.get_json(), status


class FakeSession:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.rollbacks = 0

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class FakeProfile:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.nickname = None
        self.avatar = None
        self.diagnosis = None

    def to_dict(self):
        return {
            "nickname": self.nickname,
            "avatar": self.avatar,
            "diagnosis": self.diagnosis,
        }


class FakeRiskFactorProfile:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.age = None
        self.male = None
        self.height = None
        self.weight = None
        self.current_smoker = None
        self.cigs_per_day = None
        self.bp_meds = None
        self.diabetes = None
        self.tot_chol = None
        self.glucose = None

    def to_dict(self):
        return {
            "age": self.age,
            "male": self.male,
            "height": self.height,
            "weight": self.weight,
            "current_smoker": self.current_smoker,
            "cigs_per_day": self.cigs_per_day,
            "bp_meds": self.bp_meds,
            "diabetes": self.diabetes,
            "tot_chol": self.tot_chol,
            "glucose": self.glucose,
        }


class FakeUser:
    def __init__(self, profile_obj, risk_factor_profile=None):
        self.id = 42
        self.profile = profile_obj
        self.risk_factor_profile = risk_factor_profile

    def to_dict(self):
        payload = {"id": self.id}
        if self.profile:
            payload.update(self.profile.to_dict())
        if self.risk_factor_profile:
            payload.update(self.risk_factor_profile.to_dict())
        return payload


def test_update_profile_without_data_returns_400():
    app = _app()
    user = FakeUser(FakeProfile(user_id=42))

    with app.test_request_context("/api/profile", method="PUT", json={}):
        payload, status = _json_and_status(profile.update_profile.__wrapped__(user))

    assert status == 400
    assert payload == {"error": "无数据"}


def test_update_profile_normalizes_compat_fields_and_saves(monkeypatch):
    app = _app()
    fake_session = FakeSession()
    profile_obj = FakeProfile(user_id=42)
    risk_obj = FakeRiskFactorProfile(user_id=42)
    user = FakeUser(profile_obj, risk_obj)
    monkeypatch.setattr(profile_service.db, "session", fake_session, raising=False)

    with app.test_request_context(
        "/api/profile",
        method="PUT",
        json={
            "nickname": "",
            "gender": "Female",
            "smoking": "No",
            "cholesterol": "180",
            "bp_meds": "1",
            "diabetes": False,
            "age": "56",
            "height": "170",
            "weight": "70",
            "cigs_per_day": "12",
            "diagnosis": "",
        },
    ):
        payload, status = _json_and_status(profile.update_profile.__wrapped__(user))

    assert status == 200
    assert payload["message"] == "档案已更新"
    assert profile_obj.nickname is None
    assert risk_obj.male == 0
    assert risk_obj.current_smoker == 0
    assert risk_obj.cigs_per_day == 0.0
    assert risk_obj.tot_chol == 180.0
    assert risk_obj.bp_meds == 1
    assert risk_obj.diabetes == 0
    assert profile_obj.diagnosis is None
    assert fake_session.commits == 1


def test_update_profile_rejects_range_errors():
    app = _app()
    user = FakeUser(FakeProfile(user_id=42))

    with app.test_request_context(
        "/api/profile",
        method="PUT",
        json={"age": 130},
    ):
        payload, status = _json_and_status(profile.update_profile.__wrapped__(user))

    assert status == 400
    assert payload == {"error": "年龄需在 1-120 岁之间"}


def test_update_profile_auto_creates_missing_profile(monkeypatch):
    app = _app()
    fake_session = FakeSession()
    user = FakeUser(profile_obj=None)
    monkeypatch.setattr(profile_service, "UserProfile", FakeProfile)
    monkeypatch.setattr(profile_service, "UserRiskFactorProfile", FakeRiskFactorProfile)
    monkeypatch.setattr(profile_service.db, "session", fake_session, raising=False)

    with app.test_request_context(
        "/api/profile",
        method="PUT",
        json={"gender": "Male", "smoking": "Yes", "cigs_per_day": 5},
    ):
        payload, status = _json_and_status(profile.update_profile.__wrapped__(user))

    assert status == 200
    assert payload["message"] == "档案已更新"
    assert len(fake_session.added) == 1
    assert fake_session.added[0].user_id == 42
    assert fake_session.added[0].male == 1
    assert fake_session.added[0].current_smoker == 1
    assert fake_session.added[0].cigs_per_day == 5.0
    assert fake_session.commits == 1


def test_update_profile_rejects_large_avatar():
    app = _app()
    user = FakeUser(FakeProfile(user_id=42))

    with app.test_request_context(
        "/api/profile",
        method="PUT",
        json={"avatar": "x" * (100 * 1024 + 1)},
    ):
        payload, status = _json_and_status(profile.update_profile.__wrapped__(user))

    assert status == 400
    assert payload == {"error": "头像文件过大（上限 100KB）"}


def test_profile_routes_no_longer_expose_weekly_comparison_compatibility():
    assert not hasattr(profile, "build_weekly_comparison_service")
    assert not hasattr(profile, "get_weekly_comparison")


def test_prediction_trend_route_returns_lightweight_projection(monkeypatch):
    app = _app()
    user = FakeUser(FakeProfile(user_id=42))
    calls = []

    class FakePredictionTrendUseCase:
        def execute(self, *, user_id, limit):
            calls.append((user_id, limit))
            return {
                "records": [
                    {
                        "id": 11,
                        "created_at": "2026-04-25T09:30:00",
                        "risk_probability": 0.42,
                        "risk_level": "中风险",
                    }
                ]
            }

    monkeypatch.setattr(
        profile,
        "build_prediction_trend_use_case",
        lambda: FakePredictionTrendUseCase(),
        raising=False,
    )

    with app.test_request_context("/api/profile/prediction-trend?limit=5"):
        response = profile.get_prediction_trend.__wrapped__(user)

    assert response.get_json() == {
        "records": [
            {
                "id": 11,
                "created_at": "2026-04-25T09:30:00",
                "risk_probability": 0.42,
                "risk_level": "中风险",
            }
        ]
    }
    assert calls == [(42, 5)]
