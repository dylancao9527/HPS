from extensions import db
from models import PredictionRecord

MAX_PREDICTIONS_PER_USER = 50


class PredictionRecordRetentionService:
    def enforce_prediction_limit(self, user_id):
        count = PredictionRecord.query.filter_by(user_id=user_id).count()
        if count >= MAX_PREDICTIONS_PER_USER:
            excess = count - MAX_PREDICTIONS_PER_USER + 1
            oldest = (
                PredictionRecord.query.filter_by(user_id=user_id)
                .order_by(PredictionRecord.created_at.asc())
                .limit(excess)
                .all()
            )
            for record in oldest:
                db.session.delete(record)
