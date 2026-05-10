from datetime import datetime
from types import SimpleNamespace

from flask import Flask

from routes import bp_records
from services import bp_record_service


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
        self.deleted = []
        self.commits = 0

    def add(self, record):
        self.added.append(record)

    def delete(self, record):
        self.deleted.append(record)

    def commit(self):
        self.commits += 1


class FakeField:
    def __init__(self, name):
        self.name = name

    def desc(self):
        return ("desc", self.name)

    def in_(self, values):
        return ("in", self.name, values)

    def __eq__(self, other):
        return ("eq", self.name, other)


class FakeBPRecord:
    id = FakeField("id")
    user_id = FakeField("user_id")
    recorded_at = FakeField("recorded_at")
    query = None

    def __init__(self, user_id, systolic_bp, diastolic_bp, heart_rate, recorded_at):
        self.id = 99
        self.user_id = user_id
        self.systolic_bp = systolic_bp
        self.diastolic_bp = diastolic_bp
        self.heart_rate = heart_rate
        self.recorded_at = recorded_at

    def to_dict(self):
        return {
            "id": self.id,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "heart_rate": self.heart_rate,
            "recorded_at": self.recorded_at.isoformat(),
        }


class FakeRecord:
    def __init__(self, record_id=7):
        self.id = record_id

    def to_dict(self):
        return {"id": self.id, "systolic_bp": 128, "diastolic_bp": 82}


class FakeRecordsRelationship:
    def __init__(self, pagination):
        self.pagination = pagination
        self.order_by_arg = None
        self.paginate_kwargs = None

    def order_by(self, value):
        self.order_by_arg = value
        return self

    def paginate(self, **kwargs):
        self.paginate_kwargs = kwargs
        return self.pagination


class FakeQuery:
    def __init__(self, first_result=None, deleted_count=0):
        self.first_result = first_result
        self.deleted_count = deleted_count
        self.filter_by_kwargs = None
        self.filter_args = None

    def filter_by(self, **kwargs):
        self.filter_by_kwargs = kwargs
        return self

    def filter(self, *args):
        self.filter_args = args
        return self

    def first(self):
        return self.first_result

    def delete(self, synchronize_session=False):
        self.synchronize_session = synchronize_session
        return self.deleted_count


def test_get_records_returns_paginated_records(monkeypatch, fake_user):
    app = _app()
    monkeypatch.setattr(bp_record_service, "BPRecord", FakeBPRecord)
    pagination = SimpleNamespace(items=[FakeRecord(1), FakeRecord(2)], total=2, pages=1)
    fake_user.bp_records = FakeRecordsRelationship(pagination)

    with app.test_request_context("/api/bp-records?page=2&per_page=10"):
        payload, status = _json_and_status(bp_records.get_records.__wrapped__(fake_user))

    assert status == 200
    assert payload == {
        "records": [
            {"id": 1, "systolic_bp": 128, "diastolic_bp": 82},
            {"id": 2, "systolic_bp": 128, "diastolic_bp": 82},
        ],
        "total": 2,
        "page": 2,
        "pages": 1,
    }
    assert fake_user.bp_records.order_by_arg == ("desc", "recorded_at")
    assert fake_user.bp_records.paginate_kwargs == {
        "page": 2,
        "per_page": 10,
        "error_out": False,
    }


def test_get_records_normalizes_page_size(monkeypatch, fake_user):
    app = _app()
    monkeypatch.setattr(bp_record_service, "BPRecord", FakeBPRecord)
    pagination = SimpleNamespace(items=[], total=0, pages=0)
    fake_user.bp_records = FakeRecordsRelationship(pagination)

    with app.test_request_context("/api/bp-records?page=0&per_page=9999"):
        payload, status = _json_and_status(bp_records.get_records.__wrapped__(fake_user))

    assert status == 200
    assert payload["page"] == 1
    assert fake_user.bp_records.paginate_kwargs == {
        "page": 1,
        "per_page": 100,
        "error_out": False,
    }


def test_add_record_success_commits_and_returns_record(monkeypatch, fake_user):
    app = _app()
    fake_session = FakeSession()
    monkeypatch.setattr(bp_record_service, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(bp_record_service.db, "session", fake_session, raising=False)

    with app.test_request_context(
        "/api/bp-records",
        json={
            "systolic_bp": "128",
            "diastolic_bp": "82",
            "heart_rate": "71",
            "recorded_at": "2026-04-25T09:30:00",
        },
    ):
        payload, status = _json_and_status(bp_records.add_record.__wrapped__(fake_user))

    assert status == 201
    assert payload["message"] == "记录已保存"
    assert payload["record"] == {
        "id": 99,
        "systolic_bp": 128.0,
        "diastolic_bp": 82.0,
        "heart_rate": 71.0,
        "recorded_at": "2026-04-25T09:30:00",
    }
    assert len(fake_session.added) == 1
    assert fake_session.added[0].user_id == 42
    assert fake_session.commits == 1


def test_add_record_rejects_missing_required_value(fake_user):
    app = _app()

    with app.test_request_context(
        "/api/bp-records",
        json={"diastolic_bp": 82},
    ):
        payload, status = _json_and_status(bp_records.add_record.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "收缩压为必填项"}


def test_add_record_rejects_non_numeric_heart_rate(fake_user):
    app = _app()

    with app.test_request_context(
        "/api/bp-records",
        json={"systolic_bp": 128, "diastolic_bp": 82, "heart_rate": "fast"},
    ):
        payload, status = _json_and_status(bp_records.add_record.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "心率必须为数字"}


def test_add_record_rejects_systolic_not_above_diastolic(fake_user):
    app = _app()

    with app.test_request_context(
        "/api/bp-records",
        json={"systolic_bp": 80, "diastolic_bp": 82},
    ):
        payload, status = _json_and_status(bp_records.add_record.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "收缩压应高于舒张压"}


def test_add_record_rejects_invalid_recorded_at(monkeypatch, fake_user):
    app = _app()
    fake_session = FakeSession()
    monkeypatch.setattr(bp_record_service, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(bp_record_service.db, "session", fake_session, raising=False)

    with app.test_request_context(
        "/api/bp-records",
        json={
            "systolic_bp": 128,
            "diastolic_bp": 82,
            "recorded_at": "not-a-date",
        },
    ):
        payload, status = _json_and_status(bp_records.add_record.__wrapped__(fake_user))

    assert status == 400
    assert payload == {"error": "recorded_at 格式不正确"}
    assert fake_session.added == []
    assert fake_session.commits == 0


def test_delete_record_missing_returns_404(monkeypatch, fake_user):
    app = _app()
    fake_query = FakeQuery(first_result=None)
    monkeypatch.setattr(bp_record_service, "BPRecord", FakeBPRecord)
    FakeBPRecord.query = fake_query

    with app.test_request_context("/api/bp-records/404"):
        payload, status = _json_and_status(
            bp_records.delete_record.__wrapped__(fake_user, 404)
        )

    assert status == 404
    assert payload == {"error": "记录不存在"}
    assert fake_query.filter_by_kwargs == {"id": 404, "user_id": 42}


def test_batch_delete_records_empty_ids_returns_400(fake_user):
    app = _app()

    with app.test_request_context("/api/bp-records/batch", json={"ids": []}):
        payload, status = _json_and_status(
            bp_records.batch_delete_records.__wrapped__(fake_user)
        )

    assert status == 400
    assert payload == {"error": "请选择要删除的记录"}
