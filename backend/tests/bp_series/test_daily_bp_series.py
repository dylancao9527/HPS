from datetime import date, datetime
from types import SimpleNamespace

from bp_series import repository as bp_series_repository
from bp_series.domain import (
    DailyBPSeriesPoint,
    count_leading_high_bp_days,
    is_elevated_bp,
    is_high_bp,
)
from bp_series.repository import DailyBPSeriesRepository


def test_daily_bp_series_rules_use_shared_thresholds():
    point = DailyBPSeriesPoint(
        recorded_on=date(2026, 4, 25),
        average_systolic=140,
        average_diastolic=88,
        measurements=2,
    )

    assert point.has_high_bp is True
    assert is_high_bp(139, 90) is True
    assert is_high_bp(139, 89) is False
    assert is_elevated_bp(130, 80) is True
    assert is_elevated_bp(129, 84) is False
    assert count_leading_high_bp_days(
        [
            point,
            DailyBPSeriesPoint(date(2026, 4, 24), 145, 91, 1),
            DailyBPSeriesPoint(date(2026, 4, 23), 128, 82, 1),
        ]
    ) == 2


class FakeField:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return ("eq", self.name, other)

    def __ge__(self, other):
        return ("ge", self.name, other)

    def __le__(self, other):
        return ("le", self.name, other)


class FakeDateExpression:
    def label(self, name):
        return ("label", name)

    def asc(self):
        return ("asc", "recorded_day")

    def desc(self):
        return ("desc", "recorded_day")


class FakeFunc:
    def date(self, field):
        self.date_field = field
        return FakeDateExpression()

    def avg(self, field):
        return SimpleNamespace(label=lambda name: ("avg", field.name, name))

    def count(self, field):
        return SimpleNamespace(label=lambda name: ("count", field.name, name))

    def distinct(self, field):
        return SimpleNamespace(name=("distinct", field))


class FakeAggregateQuery:
    def __init__(self, rows, scalar_value=0):
        self.rows = rows
        self.scalar_value = scalar_value
        self.filters = []

    def filter(self, *conditions):
        self.filters.extend(conditions)
        return self

    def group_by(self, *args):
        self.group_by_args = args
        return self

    def order_by(self, *args):
        self.order_by_args = args
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def all(self):
        return self.rows

    def scalar(self):
        return self.scalar_value


class FakeSession:
    def __init__(self, rows, scalar_value=0):
        self.query_obj = FakeAggregateQuery(rows, scalar_value=scalar_value)

    def query(self, *args):
        self.query_args = args
        return self.query_obj


class FakeBPRecord:
    id = FakeField("id")
    user_id = FakeField("user_id")
    recorded_at = FakeField("recorded_at")
    systolic_bp = FakeField("systolic_bp")
    diastolic_bp = FakeField("diastolic_bp")


def test_daily_bp_series_repository_reads_database_daily_projection(monkeypatch):
    rows = [
        SimpleNamespace(
            recorded_on="2026-04-20",
            average_systolic=132.0,
            average_diastolic=84.0,
            measurements=2,
        )
    ]
    fake_session = FakeSession(rows)
    fake_func = FakeFunc()
    monkeypatch.setattr(bp_series_repository, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(bp_series_repository, "func", fake_func)
    monkeypatch.setattr(
        bp_series_repository.db,
        "session",
        fake_session,
        raising=False,
    )

    points = DailyBPSeriesRepository().load_daily_series(
        user_id=42,
        start_date=date(2026, 4, 19),
        end_date=date(2026, 4, 25),
        limit=3,
        ascending=False,
    )

    assert points == [DailyBPSeriesPoint(date(2026, 4, 20), 132.0, 84.0, 2)]
    assert fake_session.query_obj.filters == [
        ("eq", "user_id", 42),
        ("ge", "recorded_at", datetime(2026, 4, 19, 0, 0)),
        ("le", "recorded_at", datetime(2026, 4, 25, 23, 59, 59, 999999)),
    ]
    assert fake_session.query_obj.order_by_args == (("desc", "recorded_day"),)
    assert fake_session.query_obj.limit_value == 3


def test_daily_bp_series_repository_counts_daily_projection_days(monkeypatch):
    fake_session = FakeSession([], scalar_value=12)
    fake_func = FakeFunc()
    monkeypatch.setattr(bp_series_repository, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(bp_series_repository, "func", fake_func)
    monkeypatch.setattr(
        bp_series_repository.db,
        "session",
        fake_session,
        raising=False,
    )

    total_days = DailyBPSeriesRepository().count_daily_series_days(user_id=42)

    assert total_days == 12
    assert fake_session.query_obj.filters == [("eq", "user_id", 42)]


def test_daily_bp_series_repository_counts_new_days_after_date(monkeypatch):
    fake_session = FakeSession([], scalar_value=2)
    fake_func = FakeFunc()
    monkeypatch.setattr(bp_series_repository, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(bp_series_repository, "func", fake_func)
    monkeypatch.setattr(
        bp_series_repository.db,
        "session",
        fake_session,
        raising=False,
    )

    new_days = DailyBPSeriesRepository().count_daily_series_days_after(
        user_id=42,
        after_date=date(2026, 4, 20),
    )

    assert new_days == 2
    assert fake_session.query_obj.filters == [
        ("eq", "user_id", 42),
        ("ge", "recorded_at", datetime(2026, 4, 21, 0, 0)),
    ]


def test_daily_bp_series_repository_loads_recent_window_in_ascending_order(monkeypatch):
    rows = [
        SimpleNamespace(
            recorded_on="2026-04-22",
            average_systolic=142.0,
            average_diastolic=91.0,
            measurements=1,
        ),
        SimpleNamespace(
            recorded_on="2026-04-21",
            average_systolic=140.0,
            average_diastolic=90.0,
            measurements=1,
        ),
        SimpleNamespace(
            recorded_on="2026-04-20",
            average_systolic=132.0,
            average_diastolic=84.0,
            measurements=2,
        ),
    ]
    fake_session = FakeSession(rows)
    fake_func = FakeFunc()
    monkeypatch.setattr(bp_series_repository, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(bp_series_repository, "func", fake_func)
    monkeypatch.setattr(
        bp_series_repository.db,
        "session",
        fake_session,
        raising=False,
    )

    points = DailyBPSeriesRepository().load_recent_daily_series(
        user_id=42,
        limit=3,
        ascending=True,
    )

    assert points == [
        DailyBPSeriesPoint(date(2026, 4, 20), 132.0, 84.0, 2),
        DailyBPSeriesPoint(date(2026, 4, 21), 140.0, 90.0, 1),
        DailyBPSeriesPoint(date(2026, 4, 22), 142.0, 91.0, 1),
    ]
    assert fake_session.query_obj.order_by_args == (("desc", "recorded_day"),)
    assert fake_session.query_obj.limit_value == 3
