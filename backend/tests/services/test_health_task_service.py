from datetime import date, datetime, timedelta
from types import SimpleNamespace

from bp_series.domain import DailyBPSeriesPoint
from services.health_task_service import HealthTaskService


def _bp_record(day):
    return SimpleNamespace(
        recorded_at=datetime(2026, 4, day, 8, 30),
        systolic_bp=148,
        diastolic_bp=92,
        heart_rate=73,
    )


def _daily(day, systolic, diastolic):
    return DailyBPSeriesPoint(
        recorded_on=date(2026, 4, day),
        average_systolic=systolic,
        average_diastolic=diastolic,
        measurements=1,
    )


class FakeHealthTaskRepository:
    def __init__(self):
        self.calls = []

    def load_today_summary_inputs(self, *, user_id, today):
        self.calls.append((user_id, today))
        return SimpleNamespace(
            latest_record=_bp_record(25),
            daily_series=[
                _daily(25, 148, 92),
                _daily(24, 145, 91),
                _daily(23, 142, 90),
                _daily(21, 132, 84),
            ],
        )


def test_today_summary_uses_projected_days_and_recent_daily_averages():
    repository = FakeHealthTaskRepository()
    service = HealthTaskService(
        now_provider=lambda: datetime(2026, 4, 25, 9, 30),
        repository=repository,
    )

    result = service.get_today_summary(user_id=42)

    assert repository.calls == [(42, date(2026, 4, 25))]
    assert result["has_record_today"] is True
    assert result["today_status_text"] == "今日已完成记录"
    assert result["current_streak_days"] == 3
    assert result["streak_status"] == "active"
    assert result["alert_level"] == "danger"
    assert result["alert_basis_days"] == 3
    assert result["latest_record"] == {
        "recorded_at": "2026-04-25T08:30:00",
        "systolic_bp": 148,
        "diastolic_bp": 92,
        "heart_rate": 73,
    }


def test_health_task_service_no_longer_exposes_raw_record_grouping_helper():
    assert not hasattr(HealthTaskService, "_group_records_by_day")
