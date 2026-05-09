from dataclasses import dataclass
from datetime import timedelta

from bp_series.domain import count_leading_high_bp_days
from bp_series.repository import DailyBPSeriesRepository
from models import BPRecord
from utils.time_utils import utc_now_naive


@dataclass(frozen=True)
class HealthTaskSummaryInputs:
    latest_record: object | None
    daily_series: list


class HealthTaskRepository:
    def __init__(self, *, daily_series_repository=None):
        self.daily_series_repository = (
            daily_series_repository or DailyBPSeriesRepository()
        )

    def load_today_summary_inputs(self, *, user_id, today):
        latest_record = (
            BPRecord.query.filter_by(user_id=user_id)
            .order_by(BPRecord.recorded_at.desc())
            .first()
        )
        daily_series = self.daily_series_repository.load_daily_series(
            user_id=user_id,
            end_date=today,
            ascending=False,
        )
        return HealthTaskSummaryInputs(
            latest_record=latest_record,
            daily_series=daily_series,
        )


class HealthTaskService:
    def __init__(self, *, now_provider=utc_now_naive, repository=None):
        self.now_provider = now_provider
        self.repository = repository or HealthTaskRepository()

    def get_today_summary(self, user_id):
        today = self.now_provider().date()
        inputs = self.repository.load_today_summary_inputs(
            user_id=user_id,
            today=today,
        )
        daily_series = list(getattr(inputs, "daily_series", None) or [])
        recorded_days = {point.recorded_on for point in daily_series}
        recent_daily_series = daily_series[:3]

        has_record_today = today in recorded_days
        current_streak_days, streak_status = self._calculate_streak(recorded_days, today)
        alert_level, alert_message, alert_basis_days = self._calculate_alert(
            recent_daily_series
        )
        latest_record = (
            self._serialize_latest_record(inputs.latest_record)
            if inputs.latest_record
            else None
        )

        if has_record_today:
            today_status_text = "今日已完成记录"
        elif streak_status == "pending_today" and current_streak_days > 0:
            today_status_text = f"已连续记录 {current_streak_days} 天，今天待补录"
        else:
            today_status_text = "今日待记录"

        if not has_record_today:
            suggested_action = "record_now"
        elif alert_level in {"warning", "danger"}:
            suggested_action = "monitor_alert"
        else:
            suggested_action = "keep_tracking"

        return {
            "has_record_today": has_record_today,
            "today_status_text": today_status_text,
            "current_streak_days": current_streak_days,
            "streak_status": streak_status,
            "alert_level": alert_level,
            "alert_message": alert_message,
            "alert_basis_days": alert_basis_days,
            "latest_record": latest_record,
            "suggested_action": suggested_action,
        }

    @staticmethod
    def _serialize_latest_record(record):
        return {
            "recorded_at": record.recorded_at.isoformat(),
            "systolic_bp": record.systolic_bp,
            "diastolic_bp": record.diastolic_bp,
            "heart_rate": record.heart_rate,
        }

    def _calculate_streak(self, recorded_days, today):
        recorded_days = set(recorded_days)
        if today in recorded_days:
            start_day = today
            streak_status = "active"
        elif today - timedelta(days=1) in recorded_days:
            start_day = today - timedelta(days=1)
            streak_status = "pending_today"
        else:
            return 0, "reset"

        streak = 0
        cursor = start_day
        while cursor in recorded_days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak, streak_status

    def _calculate_alert(self, daily_series):
        daily_series = list(daily_series or [])
        if len(daily_series) < 2:
            return "none", "暂无预警" if not daily_series else "记录不足，建议继续补充", 0

        leading_high_days = count_leading_high_bp_days(daily_series, limit=3)

        if leading_high_days >= 3:
            return "danger", "最近连续 3 天日均血压偏高，建议尽快持续监测并查看历史趋势。", 3
        if leading_high_days >= 2:
            return "warning", "最近连续 2 天日均血压偏高，建议继续监测。", 2
        return "none", "最近血压记录暂无连续偏高预警。", 0
