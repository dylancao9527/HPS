"""
==============================================================================
血压记录路由 (bp_records.py)
==============================================================================
端点：
  GET    /api/bp-records        — 获取血压记录列表（分页）
  POST   /api/bp-records        — 新增血压记录
  DELETE /api/bp-records/<id>   — 删除血压记录
==============================================================================
"""

from flask import Blueprint, request, jsonify
from routes.auth import token_required
from services.bp_record_service import BPRecordService

bp_records_bp = Blueprint("bp_records", __name__, url_prefix="/api/bp-records")
bp_record_service = BPRecordService()


def _json_result(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@bp_records_bp.route("", methods=["GET"])
@token_required
def get_records(current_user):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    return jsonify(bp_record_service.list_records(current_user, page, per_page))


@bp_records_bp.route("", methods=["POST"])
@token_required
def add_record(current_user):
    data = request.get_json() or {}
    return _json_result(bp_record_service.create_record(current_user, data))


@bp_records_bp.route("/<int:record_id>", methods=["DELETE"])
@token_required
def delete_record(current_user, record_id):
    return _json_result(bp_record_service.delete_record(current_user, record_id))


@bp_records_bp.route("/batch", methods=["DELETE"])
@token_required
def batch_delete_records(current_user):
    """批量删除血压记录"""
    data = request.get_json() or {}
    ids = data.get("ids", [])
    return _json_result(bp_record_service.batch_delete_records(current_user, ids))
