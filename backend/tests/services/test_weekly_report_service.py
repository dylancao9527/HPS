import importlib
from datetime import date, datetime
from types import SimpleNamespace

import pytest

from bp_series.domain import DailyBPSeriesPoint
from models import PredictionRecord
from services.weekly_report_service import WeeklyReportService


def _daily_bp(day, systolic, diastolic):
    return DailyBPSeriesPoint(
        recorded_on=date(2026, 4, day),
        average_systolic=systolic,
        average_diastolic=diastolic,
        measurements=1,
    )


def _prediction_record(day, risk_probability):
    return SimpleNamespace(
        created_at=datetime(2026, 4, day, 10, 0),
        risk_probability=risk_probability,
    )


class FakeWeeklyReportRepository:
    def __init__(self, daily_bp_series, prediction_records):
        self.daily_bp_series = daily_bp_series
        self.prediction_records = prediction_records

    def load_daily_series(self, **kwargs):
        self.daily_series_kwargs = kwargs
        return self.daily_bp_series

    def load_records(self, model, **kwargs):
        if model is PredictionRecord:
            return self.prediction_records
        raise AssertionError(f"unexpected model: {model}")


def test_weekly_report_summary_preserves_current_output_shape():
    service = WeeklyReportService(
        now_provider=lambda: datetime(2026, 4, 25, 9, 30),
        repository=FakeWeeklyReportRepository(
            daily_bp_series=[
                _daily_bp(12, 140, 90),
                _daily_bp(13, 140, 90),
                _daily_bp(14, 140, 90),
                _daily_bp(19, 130, 80),
                _daily_bp(20, 135, 85),
                _daily_bp(21, 140, 90),
            ],
            prediction_records=[
                _prediction_record(12, 0.4),
                _prediction_record(19, 0.2),
                _prediction_record(20, 0.3),
            ],
        ),
    )

    summary = service.build_summary(user_id=42)

    assert summary["current_period"] == "2026-04-19 ~ 2026-04-25"
    assert summary["previous_period"] == "2026-04-12 ~ 2026-04-18"
    assert summary["bp_summary"] == {
        "current_record_days": 3,
        "previous_record_days": 3,
        "current_average_systolic": 135.0,
        "previous_average_systolic": 140.0,
        "current_average_diastolic": 85.0,
        "previous_average_diastolic": 90.0,
        "enough_data": True,
    }
    assert summary["risk_summary"] == {
        "current_record_count": 2,
        "previous_record_count": 1,
        "current_average_risk_probability": 0.25,
        "previous_average_risk_probability": 0.4,
        "enough_data": True,
    }
    assert summary["adherence_summary"] == {
        "current_record_days": 3,
        "previous_record_days": 3,
        "record_change": 0,
        "enough_data": True,
    }
    assert summary["high_bp_summary"] == {
        "current_record_days": 3,
        "previous_record_days": 3,
        "current_high_bp_days": 1,
        "previous_high_bp_days": 3,
        "total_high_bp_days": 4,
        "enough_data": True,
    }
    assert summary["overall_trend_text"] == (
        "与前7天相比，最近7天平均血压下降，风险较前7天下降，记录完成天数基本持平。"
    )


def test_weekly_report_summary_preserves_insufficient_data_text():
    service = WeeklyReportService(
        now_provider=lambda: datetime(2026, 4, 25, 9, 30),
        repository=FakeWeeklyReportRepository(
            daily_bp_series=[
                _daily_bp(19, 130, 80),
                _daily_bp(20, 135, 85),
            ],
            prediction_records=[
                _prediction_record(19, 0.2),
            ],
        ),
    )

    summary = service.build_summary(user_id=42)

    assert summary["bp_summary"]["enough_data"] is False
    assert summary["risk_summary"]["enough_data"] is False
    assert summary["adherence_summary"]["enough_data"] is False
    assert summary["high_bp_summary"]["enough_data"] is False
    assert summary["overall_trend_text"] == "最近7天与前7天数据不足，请继续记录血压。"


def test_weekly_report_service_is_the_canonical_weekly_summary_entry():
    service = WeeklyReportService(
        now_provider=lambda: datetime(2026, 4, 25, 9, 30),
        repository=FakeWeeklyReportRepository(
            daily_bp_series=[
                _daily_bp(12, 140, 90),
                _daily_bp(13, 140, 90),
                _daily_bp(14, 140, 90),
                _daily_bp(19, 130, 80),
                _daily_bp(20, 135, 85),
                _daily_bp(21, 140, 90),
            ],
            prediction_records=[
                _prediction_record(12, 0.4),
                _prediction_record(19, 0.2),
            ],
        ),
    )

    summary = service.build_summary(user_id=42)

    assert summary["current_period"] == "2026-04-19 ~ 2026-04-25"
    assert summary["previous_period"] == "2026-04-12 ~ 2026-04-18"
    assert "与前7天相比" in summary["overall_trend_text"]


def test_weekly_comparison_service_module_is_removed():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("services.weekly_comparison_service")
