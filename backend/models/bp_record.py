"""
==============================================================================
血压记录模型 (BPRecord)
==============================================================================
用途：
  - 用户日常频繁录入血压数据
  - 预测时自动拉取最近一条记录
  - 积累数据后可导出 CSV 用于 Prophet 再训练
==============================================================================
"""

from extensions import db
from utils.time_utils import utc_now_naive


class BPRecord(db.Model):
    __tablename__ = 'bp_records'
    __table_args__ = (
        db.Index('ix_bp_records_user_recorded_at', 'user_id', 'recorded_at'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    systolic_bp = db.Column(db.Float, nullable=False)     # 收缩压 mmHg
    diastolic_bp = db.Column(db.Float, nullable=False)    # 舒张压 mmHg
    heart_rate = db.Column(db.Float, nullable=True)       # 心率 bpm
    recorded_at = db.Column(db.DateTime, nullable=False)  # 测量时间
    created_at = db.Column(db.DateTime, default=utc_now_naive)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'heart_rate': self.heart_rate,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
