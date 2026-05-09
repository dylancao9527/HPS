"""
==============================================================================
管理员路由 (admin.py)
==============================================================================
"""

from flask import Blueprint, request, jsonify
from routes.auth import admin_required
from services.admin_export_service import (
    build_csv_response,
    build_prediction_governance_export_download,
    build_training_export_download,
)
from services.admin_service import AdminStatsService, AdminUserService
from services.export_service import (
    export_training_csv,
)
from services.prediction_governance_service import PredictionGovernanceService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

governance_service = PredictionGovernanceService()
admin_user_service = AdminUserService()
admin_stats_service = AdminStatsService(governance_service=governance_service)


def _parse_optional_bool(raw_value):
    if raw_value is None:
        return None
    value = str(raw_value).strip().lower()
    if value in {"1", "true", "yes", "y"}:
        return True
    if value in {"0", "false", "no", "n"}:
        return False
    return None


def _json_result(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users(current_user):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    return jsonify(admin_user_service.list_users(page, per_page))


@admin_bp.route("/users/<path:account_id>", methods=["PUT"])
@admin_required
def update_user(current_user, account_id):
    data = request.get_json() or {}
    return _json_result(admin_user_service.update_account_password(account_id, data))


@admin_bp.route("/users/<path:account_id>", methods=["DELETE"])
@admin_required
def delete_user(current_user, account_id):
    return _json_result(admin_user_service.delete_user(current_user, account_id))


@admin_bp.route("/users/batch", methods=["DELETE"])
@admin_required
def batch_delete_users(current_user):
    data = request.get_json() or {}
    ids = data.get("ids", [])
    return _json_result(admin_user_service.batch_delete_users(current_user, ids))


@admin_bp.route("/export/training", methods=["GET"])
@admin_required
def export_training(current_user):
    return build_csv_response(
        build_training_export_download(export_training_csv())
    )


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats(current_user):
    return jsonify(admin_stats_service.get_stats())


@admin_bp.route("/governance/predictions", methods=["GET"])
@admin_required
def list_governance_predictions(current_user):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    risk_level = request.args.get("risk_level", "", type=str)
    confidence_level = request.args.get("confidence_level", "", type=str)
    has_anomaly = _parse_optional_bool(request.args.get("has_anomaly"))
    anomaly_type = request.args.get("anomaly_type", "", type=str)

    result = governance_service.list_predictions(
        page=page,
        per_page=per_page,
        risk_level=risk_level,
        confidence_level=confidence_level,
        has_anomaly=has_anomaly,
        anomaly_type=anomaly_type,
    )
    return jsonify(result)


@admin_bp.route("/governance/predictions/<int:prediction_id>", methods=["GET"])
@admin_required
def get_governance_prediction_detail(current_user, prediction_id):
    detail = governance_service.get_prediction_detail(prediction_id)
    if detail is None:
        return jsonify({"error": "预测记录不存在"}), 404
    return jsonify(detail)


@admin_bp.route("/governance/export", methods=["GET"])
@admin_required
def export_governance_predictions(current_user):
    risk_level = request.args.get("risk_level", "", type=str)
    confidence_level = request.args.get("confidence_level", "", type=str)
    has_anomaly = _parse_optional_bool(request.args.get("has_anomaly"))
    anomaly_type = request.args.get("anomaly_type", "", type=str)

    return build_csv_response(
        build_prediction_governance_export_download(
            governance_service.export_predictions_csv(
                risk_level=risk_level,
                confidence_level=confidence_level,
                has_anomaly=has_anomaly,
                anomaly_type=anomaly_type,
            )
        )
    )
