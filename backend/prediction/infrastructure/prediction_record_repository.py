from datetime import datetime, timedelta

from extensions import db
from models import PredictionRecord
from prediction.infrastructure.compact_prediction_mapper import (
    CompactPredictionMapper,
)


class PredictionRecordRepository:
    def __init__(self, payload_assembler, mapper=None):
        self.payload_assembler = payload_assembler
        self.mapper = mapper or CompactPredictionMapper()

    def get_prediction_history(
        self, *, user_id, page, per_page, start_date="", end_date=""
    ):
        query = (
            PredictionRecord.query.filter_by(user_id=user_id)
            .order_by(PredictionRecord.created_at.desc())
        )

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(PredictionRecord.created_at >= start_dt)
            except ValueError:
                pass
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(PredictionRecord.created_at < end_dt)
            except ValueError:
                pass

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = [
            self.payload_assembler.assemble_prediction_payload(item)
            for item in pagination.items
        ]

        return {
            "records": records,
            "total": pagination.total,
            "page": page,
            "pages": pagination.pages,
        }

    def delete_prediction(self, *, user_id, prediction_id):
        record = PredictionRecord.query.filter_by(
            id=prediction_id, user_id=user_id
        ).first()
        if not record:
            return False
        db.session.delete(record)
        db.session.commit()
        return True

    def batch_delete_predictions(self, *, user_id, prediction_ids):
        deleted = PredictionRecord.query.filter(
            PredictionRecord.id.in_(prediction_ids),
            PredictionRecord.user_id == user_id,
        ).delete(synchronize_session=False)
        db.session.commit()
        return deleted

    def list_prediction_trend(self, *, user_id, limit):
        rows = (
            db.session.query(
                PredictionRecord.id,
                PredictionRecord.created_at,
                PredictionRecord.risk_probability,
                PredictionRecord.risk_level,
            )
            .filter(PredictionRecord.user_id == user_id)
            .order_by(PredictionRecord.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": row.id,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "risk_probability": row.risk_probability,
                "risk_level": row.risk_level,
            }
            for row in rows
        ]

    def save_prediction(self, payload):
        rows = self.mapper.build_compact_prediction(payload)
        record = rows.prediction_record
        db.session.add(record)
        db.session.commit()
        return record, rows.prophet_prediction
