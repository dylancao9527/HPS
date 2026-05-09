"""
==============================================================================
管理员账号模型 (AdminUser)
==============================================================================
管理员账号独立于普通用户表，不参与健康档案、血压记录和预测记录关系。
==============================================================================
"""

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from utils.time_utils import utc_now_naive


class AdminUser(db.Model):
    """管理员账号表 —— 仅存储后台认证信息"""

    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now_naive)

    account_type = "admin"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return True

    def to_dict(self):
        return {
            "id": f"admin:{self.id}",
            "username": self.username,
            "email": self.email,
            "role": "admin",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
