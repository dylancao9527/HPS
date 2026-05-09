"""
==============================================================================
Flask 扩展实例 (extensions.py)
==============================================================================
使用 DeclarativeBase 定义命名约定，便于 Flask-Migrate 管理数据库迁移。
命名约定确保索引、约束等有规范统一的名称。
==============================================================================
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """带命名约定的 SQLAlchemy Base 类"""
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
