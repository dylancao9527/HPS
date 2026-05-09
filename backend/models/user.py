"""
==============================================================================
用户模型 (User)
==============================================================================
仅含普通用户账号相关字段：用户名、邮箱、密码。
展示资料和风险因素档案独立存储，通过一对一关系关联。

关系：
  User  1 --- 1  UserProfile            （展示资料、诊断反馈）
  User  1 --- 1  UserRiskFactorProfile  （风险因素档案）
  User  1 --- *  BPRecord      （血压记录）
  User  1 --- *  PredictionRecord（预测记录）
==============================================================================
"""

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from utils.time_utils import utc_now_naive


class User(db.Model):
    """普通用户账号表 —— 仅存储认证信息"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now_naive)

    account_type = 'user'

    # ---- 关联关系 ----
    profile = db.relationship('UserProfile', backref='user', uselist=False,
                              cascade='all, delete-orphan')
    risk_factor_profile = db.relationship(
        'UserRiskFactorProfile',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan',
    )
    bp_records = db.relationship('BPRecord', backref='user', lazy='dynamic',
                                 cascade='all, delete-orphan')
    predictions = db.relationship('PredictionRecord', backref='user', lazy='dynamic',
                                  cascade='all, delete-orphan')
    prophet_models = db.relationship('UserProphetModel', backref='user', lazy='dynamic',
                                     cascade='all, delete-orphan')

    # ---- 密码方法（werkzeug bcrypt）----
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return False

    def to_dict(self):
        """序列化：合并账号信息 + 档案信息（方便前端使用）"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': 'user',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        # 合并档案字段（如果已填写）
        if self.profile:
            data.update(self.profile.to_dict())
        else:
            data.update({
                'nickname': None,
                'avatar': None,
                'diagnosis': None,
            })
        if self.risk_factor_profile:
            data.update(self.risk_factor_profile.to_dict())
        else:
            data.update({
                'age': None,
                'male': None,
                'gender': None,
                'height': None,
                'weight': None,
                'bmi': None,
                'current_smoker': None,
                'cigs_per_day': None,
                'bp_meds': None,
                'diabetes': None,
                'smoking': None,
                'tot_chol': None,
                'cholesterol': None,
                'glucose': None,
                'profile_complete': False,
            })
        return data
