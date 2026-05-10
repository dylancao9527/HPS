from extensions import db
from utils.time_utils import utc_now_naive


class UserProphetModel(db.Model):
    __tablename__ = 'user_prophet_models'
    __table_args__ = (
        db.Index(
            'ix_user_prophet_models_active_slot_trained',
            'user_id',
            'is_active',
            'trained_at',
            'id',
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    model_version = db.Column(db.String(64), nullable=False, index=True)
    data_signature = db.Column(db.String(64), nullable=False, index=True)
    aggregation_mode = db.Column(db.String(32), nullable=False)
    trained_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    trained_until = db.Column(db.Date, nullable=False)
    data_days_used = db.Column(db.Integer, nullable=False)
    total_history_days = db.Column(db.Integer, nullable=False, default=0)
    history_window_capped = db.Column(db.Boolean, nullable=False, default=False)
    parameter_profile = db.Column(db.String(32), nullable=False)
    weekly_enabled = db.Column(db.Boolean, nullable=False, default=False)
    monthly_enabled = db.Column(db.Boolean, nullable=False, default=False)
    storage_key = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'model_version': self.model_version,
            'data_signature': self.data_signature,
            'aggregation_mode': self.aggregation_mode,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'trained_until': self.trained_until.isoformat() if self.trained_until else None,
            'data_days_used': self.data_days_used,
            'total_history_days': self.total_history_days,
            'history_window_capped': self.history_window_capped,
            'parameter_profile': self.parameter_profile,
            'weekly_enabled': self.weekly_enabled,
            'monthly_enabled': self.monthly_enabled,
            'storage_key': self.storage_key,
            'is_active': self.is_active,
        }
