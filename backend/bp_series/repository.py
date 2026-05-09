from datetime import datetime, time, timedelta

from sqlalchemy import func

from bp_series.domain import DailyBPSeriesPoint, coerce_recorded_on
from extensions import db
from models import BPRecord


class DailyBPSeriesRepository:
    def count_daily_series_days(self, *, user_id):
        recorded_day = func.date(BPRecord.recorded_at)
        total_days = (
            db.session.query(func.count(func.distinct(recorded_day)))
            .filter(BPRecord.user_id == user_id)
            .scalar()
            or 0
        )
        return int(total_days)

    def count_daily_series_days_after(self, *, user_id, after_date):
        if after_date is None:
            return 0

        recorded_day = func.date(BPRecord.recorded_at)
        start_datetime = datetime.combine(after_date + timedelta(days=1), time.min)
        total_days = (
            db.session.query(func.count(func.distinct(recorded_day)))
            .filter(BPRecord.user_id == user_id)
            .filter(BPRecord.recorded_at >= start_datetime)
            .scalar()
            or 0
        )
        return int(total_days)

    def load_daily_series(
        self,
        *,
        user_id,
        start_date=None,
        end_date=None,
        limit=None,
        ascending=True,
    ):
        recorded_day = func.date(BPRecord.recorded_at)
        query = db.session.query(
            recorded_day.label("recorded_on"),
            func.avg(BPRecord.systolic_bp).label("average_systolic"),
            func.avg(BPRecord.diastolic_bp).label("average_diastolic"),
            func.count(BPRecord.id).label("measurements"),
        ).filter(BPRecord.user_id == user_id)

        if start_date is not None:
            query = query.filter(
                BPRecord.recorded_at >= datetime.combine(start_date, time.min)
            )
        if end_date is not None:
            query = query.filter(
                BPRecord.recorded_at <= datetime.combine(end_date, time.max)
            )

        order_by_day = recorded_day.asc() if ascending else recorded_day.desc()
        query = query.group_by(recorded_day).order_by(order_by_day)
        if limit is not None:
            query = query.limit(limit)

        return [self._point_from_row(row) for row in query.all()]

    def load_recent_daily_series(self, *, user_id, limit, ascending=True):
        if limit is None:
            return self.load_daily_series(user_id=user_id, ascending=ascending)
        if limit <= 0:
            return []

        points = self.load_daily_series(
            user_id=user_id,
            limit=limit,
            ascending=False,
        )
        if ascending:
            return list(reversed(points))
        return points

    @staticmethod
    def _point_from_row(row):
        return DailyBPSeriesPoint(
            recorded_on=coerce_recorded_on(row.recorded_on),
            average_systolic=float(row.average_systolic),
            average_diastolic=float(row.average_diastolic),
            measurements=int(row.measurements),
        )
