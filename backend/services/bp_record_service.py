"""
血压记录服务。

负责血压记录的输入校验、时间归一与持久化操作；路由层只保留
request/jsonify 边界。
"""

import datetime

from extensions import db
from models import BPRecord
from prediction.domain.pagination_policy import normalize_page, normalize_per_page
from utils.time_utils import ensure_utc_naive, utc_now_naive


def _parse_required_float(value, field_name):
    if value is None or value == "":
        raise ValueError(f"{field_name}为必填项")
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name}必须为数字")


def _parse_optional_float(value, field_name):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name}必须为数字")


class BPRecordService:
    def list_records(self, user, page, per_page):
        page = normalize_page(page)
        per_page = normalize_per_page(per_page, default=20)
        pagination = user.bp_records.order_by(BPRecord.recorded_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "records": [record.to_dict() for record in pagination.items],
            "total": pagination.total,
            "page": page,
            "pages": pagination.pages,
        }

    def create_record(self, user, data):
        try:
            systolic = _parse_required_float(data.get("systolic_bp"), "收缩压")
            diastolic = _parse_required_float(data.get("diastolic_bp"), "舒张压")
            heart_rate = _parse_optional_float(data.get("heart_rate"), "心率")
        except ValueError as exc:
            return {"error": str(exc)}, 400

        validation_error = self._validate_measurements(
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate,
        )
        if validation_error:
            return {"error": validation_error}, 400

        try:
            recorded_at = self._parse_recorded_at(data.get("recorded_at"))
        except ValueError as exc:
            return {"error": str(exc)}, 400

        record = BPRecord(
            user_id=user.id,
            systolic_bp=systolic,
            diastolic_bp=diastolic,
            heart_rate=heart_rate,
            recorded_at=recorded_at,
        )
        db.session.add(record)
        db.session.commit()

        return {"message": "记录已保存", "record": record.to_dict()}, 201

    def delete_record(self, user, record_id):
        record = BPRecord.query.filter_by(id=record_id, user_id=user.id).first()
        if not record:
            return {"error": "记录不存在"}, 404

        db.session.delete(record)
        db.session.commit()
        return {"message": "已删除"}

    def batch_delete_records(self, user, ids):
        if not ids:
            return {"error": "请选择要删除的记录"}, 400

        deleted = BPRecord.query.filter(
            BPRecord.id.in_(ids),
            BPRecord.user_id == user.id,
        ).delete(synchronize_session=False)
        db.session.commit()
        return {"message": f"已删除 {deleted} 条记录"}

    def _parse_recorded_at(self, recorded_at_str):
        if recorded_at_str is None:
            return ensure_utc_naive(utc_now_naive())
        if isinstance(recorded_at_str, datetime.datetime):
            return ensure_utc_naive(recorded_at_str)

        try:
            recorded_at = datetime.datetime.fromisoformat(recorded_at_str)
        except (TypeError, ValueError):
            raise ValueError("recorded_at 格式不正确")

        return ensure_utc_naive(recorded_at)

    def _validate_measurements(self, *, systolic, diastolic, heart_rate):
        if not (60 <= systolic <= 300):
            return "收缩压需在 60-300 mmHg 之间"
        if not (30 <= diastolic <= 200):
            return "舒张压需在 30-200 mmHg 之间"
        if systolic <= diastolic:
            return "收缩压应高于舒张压"
        if heart_rate is not None and not (30 <= heart_rate <= 220):
            return "心率需在 30-220 bpm 之间"
        return None
