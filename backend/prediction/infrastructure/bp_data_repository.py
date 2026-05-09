from extensions import db
from models import BPRecord, User
from prediction.domain.bp_data_policy import build_bp_data_status
from sqlalchemy import func


class BPDataRepository:
    def get_user(self, user_id):
        return db.session.get(User, user_id)

    def get_latest_bp_record(self, user_id):
        return (
            BPRecord.query.filter_by(user_id=user_id)
            .order_by(BPRecord.recorded_at.desc())
            .first()
        )

    def get_bp_data_status(self, *, user_id, forecast_days):
        total_records = BPRecord.query.filter_by(user_id=user_id).count()
        total_days = (
            db.session.query(
                func.count(func.distinct(func.date(BPRecord.recorded_at)))
            )
            .filter(BPRecord.user_id == user_id)
            .scalar()
            or 0
        )
        return build_bp_data_status(
            total_records=total_records,
            total_days=total_days,
            forecast_days=forecast_days,
        )
