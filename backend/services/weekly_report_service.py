"""Canonical weekly health report service."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from bp_series.repository import DailyBPSeriesRepository
from models import BPRecord, PredictionRecord
from utils.time_utils import utc_now_naive


@dataclass(frozen=True)
class Window:
    start_date: date
    end_date: date


class WeeklyReportRepository:
    def __init__(self, *, daily_series_repository=None):
        self.daily_series_repository = (
            daily_series_repository or DailyBPSeriesRepository()
        )

    def load_daily_series(self, *, user_id, window_start, window_end):
        return self.daily_series_repository.load_daily_series(
            user_id=user_id,
            start_date=window_start,
            end_date=window_end,
            ascending=True,
        )

    def load_records(self, model, *, user_id, date_field, window_start, window_end):
        window_start_dt = datetime.combine(window_start, time.min)
        window_end_dt = datetime.combine(window_end, time.max)
        return (
            model.query.filter(model.user_id == user_id)
            .filter(date_field >= window_start_dt)
            .filter(date_field <= window_end_dt)
            .order_by(date_field.asc())
            .all()
        )


class WeeklyReportCalculator:
    def build_windows(self, today):
        current_window = Window(start_date=today - timedelta(days=6), end_date=today)
        previous_window = Window(
            start_date=today - timedelta(days=13),
            end_date=today - timedelta(days=7),
        )
        return current_window, previous_window

    def build_summary(self, *, today, daily_bp_series, prediction_records):
        current_window, previous_window = self.build_windows(today)
        bp_summary = self._build_bp_summary(
            daily_bp_series, current_window, previous_window
        )
        risk_summary = self._build_risk_summary(
            prediction_records, current_window, previous_window
        )
        adherence_summary = self._build_adherence_summary(
            daily_bp_series, current_window, previous_window
        )
        high_bp_summary = self._build_high_bp_summary(
            daily_bp_series, current_window, previous_window
        )

        return {
            "current_period": f"{current_window.start_date.isoformat()} ~ {current_window.end_date.isoformat()}",
            "previous_period": f"{previous_window.start_date.isoformat()} ~ {previous_window.end_date.isoformat()}",
            "bp_summary": bp_summary,
            "risk_summary": risk_summary,
            "adherence_summary": adherence_summary,
            "high_bp_summary": high_bp_summary,
            "overall_trend_text": self._build_overall_text(
                bp_summary,
                risk_summary,
                adherence_summary,
                high_bp_summary,
            ),
        }

    @staticmethod
    def _split_daily_series_by_window(points, *, current_window, previous_window):
        current_points = []
        previous_points = []

        for point in points:
            if current_window.start_date <= point.recorded_on <= current_window.end_date:
                current_points.append(point)
            elif previous_window.start_date <= point.recorded_on <= previous_window.end_date:
                previous_points.append(point)

        return current_points, previous_points

    @staticmethod
    def _split_records_by_window(records, *, date_attr, current_window, previous_window):
        current_records = []
        previous_records = []

        for record in records:
            record_date = getattr(record, date_attr).date()
            if current_window.start_date <= record_date <= current_window.end_date:
                current_records.append(record)
            elif previous_window.start_date <= record_date <= previous_window.end_date:
                previous_records.append(record)

        return current_records, previous_records

    @staticmethod
    def _average(values):
        if not values:
            return None
        return sum(values) / len(values)

    @staticmethod
    def _aggregate_risk_by_day(records):
        daily = {}
        for record in records:
            record_date = record.created_at.date()
            daily.setdefault(record_date, []).append(record.risk_probability)

        return [
            {
                "date": record_date,
                "average_risk_probability": WeeklyReportCalculator._average(values),
            }
            for record_date, values in sorted(daily.items())
        ]

    def _build_bp_summary(self, daily_bp_series, current_window, previous_window):
        current_daily, previous_daily = self._split_daily_series_by_window(
            daily_bp_series,
            current_window=current_window,
            previous_window=previous_window,
        )
        current_days = len(current_daily)
        previous_days = len(previous_daily)

        return {
            "current_record_days": current_days,
            "previous_record_days": previous_days,
            "current_average_systolic": self._average(
                [day.average_systolic for day in current_daily]
            ),
            "previous_average_systolic": self._average(
                [day.average_systolic for day in previous_daily]
            ),
            "current_average_diastolic": self._average(
                [day.average_diastolic for day in current_daily]
            ),
            "previous_average_diastolic": self._average(
                [day.average_diastolic for day in previous_daily]
            ),
            "enough_data": self._has_weekly_bp_comparison_data(
                current_days, previous_days
            ),
        }

    def _build_risk_summary(self, prediction_records, current_window, previous_window):
        current_records, previous_records = self._split_records_by_window(
            prediction_records,
            date_attr="created_at",
            current_window=current_window,
            previous_window=previous_window,
        )
        current_daily = self._aggregate_risk_by_day(current_records)
        previous_daily = self._aggregate_risk_by_day(previous_records)

        return {
            "current_record_count": len(current_daily),
            "previous_record_count": len(previous_daily),
            "current_average_risk_probability": self._average(
                [day["average_risk_probability"] for day in current_daily]
            ),
            "previous_average_risk_probability": self._average(
                [day["average_risk_probability"] for day in previous_daily]
            ),
            "enough_data": self._has_weekly_risk_comparison_data(
                len(current_daily), len(previous_daily)
            ),
        }

    def _build_adherence_summary(self, daily_bp_series, current_window, previous_window):
        current_daily, previous_daily = self._split_daily_series_by_window(
            daily_bp_series,
            current_window=current_window,
            previous_window=previous_window,
        )
        current_days = len(current_daily)
        previous_days = len(previous_daily)

        return {
            "current_record_days": current_days,
            "previous_record_days": previous_days,
            "record_change": current_days - previous_days,
            "enough_data": self._has_weekly_bp_comparison_data(
                current_days, previous_days
            ),
        }

    def _build_high_bp_summary(self, daily_bp_series, current_window, previous_window):
        current_daily, previous_daily = self._split_daily_series_by_window(
            daily_bp_series,
            current_window=current_window,
            previous_window=previous_window,
        )
        current_days = len(current_daily)
        previous_days = len(previous_daily)
        current_high_bp_days = sum(1 for day in current_daily if day.has_high_bp)
        previous_high_bp_days = sum(1 for day in previous_daily if day.has_high_bp)

        return {
            "current_record_days": current_days,
            "previous_record_days": previous_days,
            "current_high_bp_days": current_high_bp_days,
            "previous_high_bp_days": previous_high_bp_days,
            "total_high_bp_days": current_high_bp_days + previous_high_bp_days,
            "enough_data": self._has_weekly_bp_comparison_data(
                current_days, previous_days
            ),
        }

    @staticmethod
    def _build_overall_text(bp_summary, risk_summary, adherence_summary, high_bp_summary):
        if not (
            bp_summary["enough_data"]
            and risk_summary["enough_data"]
            and adherence_summary["enough_data"]
            and high_bp_summary["enough_data"]
        ):
            return "最近7天与前7天数据不足，请继续记录血压。"

        bp_clause = WeeklyReportCalculator._describe_change(
            bp_summary["current_average_systolic"],
            bp_summary["previous_average_systolic"],
            positive_text="最近7天平均血压上升",
            negative_text="最近7天平均血压下降",
            neutral_text="最近7天平均血压基本持平",
        )
        risk_clause = WeeklyReportCalculator._describe_change(
            risk_summary["current_average_risk_probability"],
            risk_summary["previous_average_risk_probability"],
            positive_text="风险较前7天上升",
            negative_text="风险较前7天下降",
            neutral_text="风险基本持平",
        )
        adherence_clause = WeeklyReportCalculator._describe_change(
            adherence_summary["current_record_days"],
            adherence_summary["previous_record_days"],
            positive_text="记录完成天数增加",
            negative_text="记录完成天数减少",
            neutral_text="记录完成天数基本持平",
        )

        return f"与前7天相比，{bp_clause}，{risk_clause}，{adherence_clause}。"

    @staticmethod
    def _describe_change(
        current_value,
        previous_value,
        *,
        positive_text,
        negative_text,
        neutral_text,
    ):
        if current_value > previous_value:
            return positive_text
        if current_value < previous_value:
            return negative_text
        return neutral_text

    @staticmethod
    def _has_weekly_bp_comparison_data(current_days, previous_days):
        return current_days >= 3 and previous_days >= 3

    @staticmethod
    def _has_weekly_risk_comparison_data(current_count, previous_count):
        return current_count > 0 and previous_count > 0


class WeeklyReportService:
    def __init__(
        self,
        *,
        now_provider=utc_now_naive,
        repository=None,
        calculator=None,
    ):
        self.now_provider = now_provider
        self.repository = repository or WeeklyReportRepository()
        self.calculator = calculator or WeeklyReportCalculator()

    def build_summary(self, user_id):
        today = self.now_provider().date()
        current_window, previous_window = self.calculator.build_windows(today)

        daily_bp_series = self.repository.load_daily_series(
            user_id=user_id,
            window_start=previous_window.start_date,
            window_end=current_window.end_date,
        )
        prediction_records = self.repository.load_records(
            PredictionRecord,
            user_id=user_id,
            date_field=PredictionRecord.created_at,
            window_start=previous_window.start_date,
            window_end=current_window.end_date,
        )

        return self.calculator.build_summary(
            today=today,
            daily_bp_series=daily_bp_series,
            prediction_records=prediction_records,
        )


__all__ = [
    "BPRecord",
    "PredictionRecord",
    "WeeklyReportCalculator",
    "WeeklyReportRepository",
    "WeeklyReportService",
    "Window",
]
