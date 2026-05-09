from extensions import db
from utils.time_utils import utc_now_naive


class PredictionRecord(db.Model):
    """一次 7 天风险预测的紧凑历史记录。"""

    __tablename__ = 'prediction_records'
    __table_args__ = (
        db.Index('ix_prediction_records_user_created_at', 'user_id', 'created_at'),
        db.Index('ix_prediction_records_risk_created_at', 'risk_level', 'created_at'),
        db.Index('ix_prediction_records_confidence_created_at', 'confidence_level', 'created_at'),
        db.Index('ix_prediction_records_anomaly_created_at', 'has_anomaly', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    risk_probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    data_days_used = db.Column(db.Integer, nullable=True)
    confidence_level = db.Column(db.String(16), nullable=True)
    cache_mode = db.Column(db.String(32), nullable=False, default='fresh_train')
    has_anomaly = db.Column(db.Boolean, nullable=False, default=False)
    input_snapshot = db.Column(db.JSON, nullable=True)
    fusion_meta = db.Column(db.JSON, nullable=True)
    bp_forecast = db.Column(db.JSON, nullable=True)
    training_meta = db.Column(db.JSON, nullable=True)
    recommendations = db.Column(db.JSON, nullable=True)
    anomaly_flags = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now_naive)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'risk_probability': self.risk_probability,
            'risk_level': self.risk_level,
            'data_days_used': self.data_days_used,
            'confidence_level': self.confidence_level,
            'cache_mode': self.cache_mode,
            'has_anomaly': self.has_anomaly,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
