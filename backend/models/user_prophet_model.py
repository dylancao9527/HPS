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
    model_version = db.Column(db.String(64), nullable=False)
    data_signature = db.Column(db.String(64), nullable=False)
    trained_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    trained_until = db.Column(db.Date, nullable=False)
    storage_key = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'model_version': self.model_version,
            'data_signature': self.data_signature,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'trained_until': self.trained_until.isoformat() if self.trained_until else None,
            'storage_key': self.storage_key,
            'is_active': self.is_active,
        }
