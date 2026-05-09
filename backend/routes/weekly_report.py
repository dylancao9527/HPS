from flask import Blueprint, jsonify

from routes.auth import token_required
from services.weekly_report_service import WeeklyReportService

weekly_report_bp = Blueprint("weekly_report", __name__, url_prefix="/api/weekly-report")


def build_weekly_report_service():
    return WeeklyReportService()


@weekly_report_bp.route("", methods=["GET"])
@token_required
def get_weekly_report(current_user):
    """返回普通用户的周健康报告，固定比较最近7天与前7天。"""
    return jsonify(build_weekly_report_service().build_summary(current_user.id))
