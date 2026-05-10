from datetime import datetime
from types import SimpleNamespace

from flask import Flask

from routes import admin
from services import admin_service


def _app():
    return Flask(__name__)


def _json_and_status(result):
    if isinstance(result, tuple):
        response, status = result
    else:
        response, status = result, 200
    return response.get_json(), status


class FakeSession:
    def __init__(self, get_result=None):
        self.get_result = get_result
        self.deleted = []
        self.commits = 0

    def get(self, model, item_id):
        self.get_call = (model, item_id)
        return self.get_result

    def delete(self, item):
        self.deleted.append(item)

    def commit(self):
        self.commits += 1


class FakeField:
    def __init__(self, name):
        self.name = name

    def desc(self):
        return ("desc", self.name)

    def in_(self, values):
        return ("in", self.name, values)

    def __ge__(self, other):
        return ("ge", self.name, other)


class FakeUser:
    def __init__(self, user_id, username="user", email="user@example.com"):
        self.id = user_id
        self.username = username
        self.email = email
        self.passwords = []

    def set_password(self, password):
        self.passwords.append(password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": "user",
        }


class FakeAdminUser(FakeUser):
    @property
    def is_admin(self):
        return True

    def to_dict(self):
        return {
            "id": f"admin:{self.id}",
            "username": self.username,
            "email": self.email,
            "role": "admin",
        }


class FakeListQuery:
    def __init__(self, items=None, count_value=0):
        self.items = items or []
        self.count_value = count_value

    def order_by(self, value):
        self.order_by_arg = value
        return self

    def paginate(self, **kwargs):
        self.paginate_kwargs = kwargs
        return SimpleNamespace(items=self.items, total=len(self.items), pages=1)

    def count(self):
        return self.count_value

    def filter(self, *args):
        self.filter_args = args
        return self

    def all(self):
        return self.items


class FakeUserModel:
    id = FakeField("id")
    created_at = FakeField("created_at")
    query = None


class FakeAdminUserModel:
    created_at = FakeField("created_at")
    query = None


class FakeGovernanceService:
    def get_summary(self):
        return {"total_review_items": 3}


class RecordingGovernanceService:
    def __init__(self):
        self.list_kwargs = None
        self.export_kwargs = None

    def list_predictions(self, **kwargs):
        self.list_kwargs = kwargs
        return {"records": [], "total": 0, "page": kwargs["page"], "pages": 0}

    def export_predictions_csv(self, **kwargs):
        self.export_kwargs = kwargs
        return "prediction_id\n"


def test_get_users_returns_paginated_users(monkeypatch):
    app = _app()
    FakeUserModel.query = FakeListQuery(
        items=[FakeUser(1, "alice"), FakeUser(2, "bob")]
    )
    FakeAdminUserModel.query = FakeListQuery(items=[FakeAdminUser(1, "root")])
    monkeypatch.setattr(admin_service, "User", FakeUserModel)
    monkeypatch.setattr(admin_service, "AdminUser", FakeAdminUserModel)

    with app.test_request_context("/api/admin/users?page=2&per_page=10"):
        payload, status = _json_and_status(
            admin.get_users.__wrapped__(FakeAdminUser(99, "admin"))
        )

    assert status == 200
    assert payload == {
        "users": [
            {
                "id": 1,
                "username": "alice",
                "email": "user@example.com",
                "role": "user",
            },
            {
                "id": 2,
                "username": "bob",
                "email": "user@example.com",
                "role": "user",
            },
        ],
        "admins": [
            {
                "id": "admin:1",
                "username": "root",
                "email": "user@example.com",
                "role": "admin",
            }
        ],
        "total": 2,
        "admin_total": 1,
        "page": 2,
        "pages": 1,
    }
    assert FakeUserModel.query.order_by_arg == ("desc", "created_at")
    assert FakeUserModel.query.paginate_kwargs == {
        "page": 2,
        "per_page": 10,
        "error_out": False,
    }


def test_get_users_normalizes_page_size(monkeypatch):
    app = _app()
    FakeUserModel.query = FakeListQuery()
    FakeAdminUserModel.query = FakeListQuery()
    monkeypatch.setattr(admin_service, "User", FakeUserModel)
    monkeypatch.setattr(admin_service, "AdminUser", FakeAdminUserModel)

    with app.test_request_context("/api/admin/users?page=-1&per_page=9999"):
        payload, status = _json_and_status(
            admin.get_users.__wrapped__(FakeAdminUser(99, "admin"))
        )

    assert status == 200
    assert payload["page"] == 1
    assert FakeUserModel.query.paginate_kwargs == {
        "page": 1,
        "per_page": 100,
        "error_out": False,
    }


def test_update_user_only_allows_password_change(monkeypatch):
    app = _app()
    target = FakeUser(7, "target", "target@example.com")
    fake_session = FakeSession(get_result=target)
    monkeypatch.setattr(admin_service.db, "session", fake_session, raising=False)
    monkeypatch.setattr(admin_service, "User", FakeUserModel)

    with app.test_request_context(
        "/api/admin/users/7",
        method="PUT",
        json={"password": "Newpass123!"},
    ):
        payload, status = _json_and_status(
            admin.update_user.__wrapped__(FakeAdminUser(99, "admin"), 7)
        )

    assert status == 200
    assert payload == {
        "message": "用户密码已更新",
        "user": {
            "id": 7,
            "username": "target",
            "email": "target@example.com",
            "role": "user",
        },
    }
    assert target.passwords == ["Newpass123!"]
    assert fake_session.commits == 1


def test_update_user_rejects_username_or_email_change(monkeypatch):
    app = _app()
    target = FakeUser(7, "target", "target@example.com")
    monkeypatch.setattr(
        admin_service.db,
        "session",
        FakeSession(get_result=target),
        raising=False,
    )
    monkeypatch.setattr(admin_service, "User", FakeUserModel)

    with app.test_request_context(
        "/api/admin/users/7",
        method="PUT",
        json={"username": "other", "password": "Newpass123!"},
    ):
        payload, status = _json_and_status(
            admin.update_user.__wrapped__(FakeAdminUser(99, "admin"), 7)
        )

    assert status == 400
    assert payload == {"error": "管理员仅可修改密码，不能修改用户名或邮箱"}


def test_update_user_missing_returns_404(monkeypatch):
    app = _app()
    monkeypatch.setattr(
        admin_service.db,
        "session",
        FakeSession(get_result=None),
        raising=False,
    )
    monkeypatch.setattr(admin_service, "User", FakeUserModel)

    with app.test_request_context("/api/admin/users/404", method="PUT", json={}):
        payload, status = _json_and_status(
            admin.update_user.__wrapped__(FakeAdminUser(99, "admin"), 404)
        )

    assert status == 404
    assert payload == {"error": "用户不存在"}


def test_delete_user_rejects_admin_account_delete():
    app = _app()

    with app.test_request_context("/api/admin/users/admin:1", method="DELETE"):
        payload, status = _json_and_status(
            admin.delete_user.__wrapped__(FakeAdminUser(1, "admin"), "admin:1")
        )

    assert status == 400
    assert payload == {"error": "管理员账号不能在用户管理中删除"}


def test_delete_user_success(monkeypatch):
    app = _app()
    target = FakeUser(7, "target")
    fake_session = FakeSession(get_result=target)
    monkeypatch.setattr(admin_service.db, "session", fake_session, raising=False)
    monkeypatch.setattr(admin_service, "User", FakeUserModel)

    with app.test_request_context("/api/admin/users/7", method="DELETE"):
        payload, status = _json_and_status(
            admin.delete_user.__wrapped__(FakeAdminUser(99, "admin"), 7)
        )

    assert status == 200
    assert payload == {"message": "用户 target 已删除"}
    assert fake_session.deleted == [target]
    assert fake_session.commits == 1


def test_batch_delete_users_filters_current_admin(monkeypatch):
    app = _app()
    fake_session = FakeSession()
    users_to_delete = [FakeUser(2, "two"), FakeUser(3, "three")]
    FakeUserModel.query = FakeListQuery(items=users_to_delete)
    monkeypatch.setattr(admin_service, "User", FakeUserModel)
    monkeypatch.setattr(admin_service.db, "session", fake_session, raising=False)

    with app.test_request_context(
        "/api/admin/users/batch",
        method="DELETE",
        json={"ids": [1, 2, 3]},
    ):
        payload, status = _json_and_status(
            admin.batch_delete_users.__wrapped__(FakeAdminUser(1, "admin"))
        )

    assert status == 200
    assert payload == {"message": "已删除 2 个用户"}
    assert FakeUserModel.query.filter_args == (("in", "id", [1, 2, 3]),)
    assert fake_session.deleted == users_to_delete
    assert fake_session.commits == 1


def test_get_stats_returns_admin_dashboard_shape(monkeypatch):
    app = _app()
    user_query = FakeListQuery(count_value=10)

    class UserModel:
        created_at = FakeField("created_at")
        query = user_query

    class BPRecordModel:
        query = FakeListQuery(count_value=22)

    class PredictionModel:
        created_at = FakeField("created_at")
        query = FakeListQuery(count_value=8)

    monkeypatch.setattr(admin_service, "User", UserModel)
    monkeypatch.setattr(admin_service, "BPRecord", BPRecordModel)
    monkeypatch.setattr(admin_service, "PredictionRecord", PredictionModel)
    monkeypatch.setattr(
        admin,
        "admin_stats_service",
        admin_service.AdminStatsService(
            governance_service=FakeGovernanceService(),
            now_provider=lambda: datetime(2026, 4, 25, 9, 30),
            training_export_stats_provider=lambda: {"exportable_samples": 5},
        ),
    )

    with app.test_request_context("/api/admin/stats"):
        payload, status = _json_and_status(
            admin.get_stats.__wrapped__(FakeAdminUser(99, "admin"))
        )

    assert status == 200
    assert payload == {
        "total_users": 10,
        "total_bp_records": 22,
        "total_predictions": 8,
        "today_users": 10,
        "today_predictions": 8,
        "training_export": {"exportable_samples": 5},
        "governance": {"total_review_items": 3},
    }


def test_list_governance_predictions_passes_anomaly_type(monkeypatch):
    app = _app()
    recording = RecordingGovernanceService()
    monkeypatch.setattr(admin, "governance_service", recording)

    with app.test_request_context(
        "/api/admin/governance/predictions?anomaly_type=high_risk_low_confidence"
    ):
        payload, status = _json_and_status(
            admin.list_governance_predictions.__wrapped__(FakeAdminUser(99, "admin"))
        )

    assert status == 200
    assert payload == {"records": [], "total": 0, "page": 1, "pages": 0}
    assert recording.list_kwargs["anomaly_type"] == "high_risk_low_confidence"


def test_export_governance_predictions_passes_anomaly_type(monkeypatch):
    app = _app()
    recording = RecordingGovernanceService()
    monkeypatch.setattr(admin, "governance_service", recording)

    with app.test_request_context(
        "/api/admin/governance/export?anomaly_type=insufficient_data_prediction"
    ):
        response = admin.export_governance_predictions.__wrapped__(
            FakeAdminUser(99, "admin")
        )

    assert response.get_data(as_text=True) == "prediction_id\n"
    assert recording.export_kwargs["anomaly_type"] == "insufficient_data_prediction"
