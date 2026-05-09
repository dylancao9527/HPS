from types import SimpleNamespace

from flask import Flask

from models.user_profile import UserRiskFactorProfile
from prediction.schemas.input_snapshot import PredictionInputSnapshot
from services import profile_service
from training import export_samples


def _app():
    return Flask(__name__)


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
    __slots__ = ("user_id", "nickname", "avatar", "diagnosis")

    def __init__(self, user_id=None):
        self.user_id = user_id
        self.nickname = None
        self.avatar = None
        self.diagnosis = None


class FakeRiskFactorProfile:
    __slots__ = (
        "user_id",
        "age",
        "male",
        "height",
        "weight",
        "current_smoker",
        "cigs_per_day",
        "bp_meds",
        "diabetes",
        "tot_chol",
        "glucose",
    )

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


class FakeUser:
    def __init__(self):
        self.id = 42
        self.profile = None
        self.risk_factor_profile = None

    def to_dict(self):
        return {"id": self.id}


def test_profile_service_writes_identity_and_risk_factors_to_separate_records(monkeypatch):
    app = _app()
    user = FakeUser()
    fake_session = FakeSession()
    monkeypatch.setattr(profile_service, "UserProfile", FakeProfile)
    monkeypatch.setattr(profile_service, "UserRiskFactorProfile", FakeRiskFactorProfile)
    monkeypatch.setattr(profile_service.db, "session", fake_session, raising=False)

    payload_data = {
            "nickname": "Alice",
            "diagnosis": "No",
            "age": "56",
            "gender": "Female",
            "height": "170",
            "weight": "70",
            "smoking": "No",
            "cigs_per_day": "12",
            "bp_meds": "1",
            "diabetes": False,
            "tot_chol": "180",
            "glucose": "96",
        }

    with app.test_request_context("/api/profile", method="PUT", json=payload_data):
        result = profile_service.ProfileService().update_profile(user, payload_data)

    assert result["message"] == "档案已更新"
    assert len(fake_session.added) == 2
    profile, risk = fake_session.added
    assert profile.nickname == "Alice"
    assert profile.diagnosis == "No"
    assert risk.age == 56.0
    assert risk.male == 0
    assert risk.current_smoker == 0
    assert risk.cigs_per_day == 0.0
    assert risk.bp_meds == 1
    assert risk.diabetes == 0
    assert risk.tot_chol == 180.0
    assert risk.glucose == 96.0
    assert fake_session.commits == 1


def test_prediction_input_snapshot_reads_risk_factor_profile_not_diagnosis_profile():
    user = SimpleNamespace(
        profile=SimpleNamespace(diagnosis="Yes"),
        risk_factor_profile=SimpleNamespace(
            age=58,
            male=1,
            bmi=25.1,
            current_smoker=0,
            cigs_per_day=8,
            bp_meds=1,
            diabetes=0,
            tot_chol=188,
            glucose=94,
            profile_complete=True,
        ),
    )
    latest_bp = SimpleNamespace(systolic_bp=136, diastolic_bp=84, heart_rate=72)

    snapshot = PredictionInputSnapshot.from_user_and_latest_bp(
        user=user,
        latest_bp=latest_bp,
    )

    assert snapshot.age == 58
    assert snapshot.bmi == 25.1
    assert snapshot.current_smoker == 0
    assert snapshot.cigs_per_day == 0
    assert not hasattr(snapshot, "diagnosis")


def test_risk_factor_profile_minimum_completeness_does_not_require_smoking_fields():
    risk_profile = UserRiskFactorProfile(
        age=58,
        male=1,
        height=170,
        weight=72,
        current_smoker=None,
        cigs_per_day=None,
        bp_meds=None,
        diabetes=None,
        tot_chol=None,
        glucose=None,
    )
    user = SimpleNamespace(risk_factor_profile=risk_profile)
    latest_bp = SimpleNamespace(systolic_bp=136, diastolic_bp=84, heart_rate=72)

    snapshot = PredictionInputSnapshot.from_user_and_latest_bp(
        user=user,
        latest_bp=latest_bp,
    )

    assert risk_profile.profile_complete is True
    assert snapshot.current_smoker is None
    assert snapshot.cigs_per_day is None


def test_training_export_projection_uses_diagnosis_profile_and_risk_factor_profile():
    projection = export_samples.TrainingExportProjection(
        user_id=1,
        profile=SimpleNamespace(diagnosis="No"),
        risk_factor_profile=SimpleNamespace(
            profile_complete=True,
            age=56,
            male=1,
            bmi=24.2,
            current_smoker=0,
            cigs_per_day=8,
            bp_meds=1,
            diabetes=0,
            tot_chol=190,
            glucose=96,
        ),
        recent_bp={
            "systolic": 132,
            "diastolic": 82,
            "heart_rate": 71,
            "count_used": 5,
        },
        total_bp_count=5,
        high_bp_count=0,
    )

    sample = export_samples.build_training_export_sample_from_projection(projection)

    assert sample.label == 0
    assert sample.label_source == "diagnosis"
    assert sample.row["age"] == 56
    assert sample.row["cigsPerDay"] == 0
