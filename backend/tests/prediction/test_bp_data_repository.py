from prediction.infrastructure import bp_data_repository
from prediction.infrastructure.bp_data_repository import BPDataRepository


class FakeField:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return ("eq", self.name, other)


class FakeRecordCountQuery:
    def __init__(self, count):
        self._count = count

    def filter_by(self, **kwargs):
        self.filter_by_kwargs = kwargs
        return self

    def count(self):
        return self._count

    def all(self):
        raise AssertionError("bp data status should use aggregate counts, not load records")


class FakeDistinctDayQuery:
    def __init__(self, total_days):
        self.total_days = total_days

    def filter(self, *conditions):
        self.filter_conditions = conditions
        return self

    def scalar(self):
        return self.total_days


class FakeSession:
    def __init__(self, total_days):
        self.total_days = total_days

    def query(self, *args):
        self.query_args = args
        return FakeDistinctDayQuery(self.total_days)


class FakeBPRecord:
    user_id = FakeField("user_id")
    recorded_at = FakeField("recorded_at")
    query = FakeRecordCountQuery(12)


def test_bp_data_status_uses_count_aggregates_without_loading_records(monkeypatch):
    monkeypatch.setattr(bp_data_repository, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(
        bp_data_repository.db,
        "session",
        FakeSession(total_days=4),
        raising=False,
    )

    result = BPDataRepository().get_bp_data_status(user_id=42, forecast_days=7)

    assert FakeBPRecord.query.filter_by_kwargs == {"user_id": 42}
    assert result["total_records"] == 12
    assert result["total_days"] == 4
    assert result["status"] == "warning"
