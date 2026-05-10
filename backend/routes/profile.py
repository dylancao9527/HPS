"""
==============================================================================
个人档案路由 (profile.py)
==============================================================================
端点：
  GET  /api/profile  — 获取当前用户档案
  PUT  /api/profile  — 更新档案（自动创建 UserProfile 行如果不存在）

注意：
  User 表只存账号信息，健康数据存在 UserProfile 表中。
  前端访问 /api/auth/me 获得的 user 对象已包含档案字段（User.to_dict 合并了）。
==============================================================================
"""

from flask import Blueprint, request, jsonify
from prediction.application.composition import PredictionUseCaseFactory
from prediction.domain.pagination_policy import normalize_per_page
from routes.auth import token_required
from services.profile_service import ProfileService
from services.weekly_report_service import WeeklyReportService

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")
profile_service = ProfileService()
prediction_use_cases = PredictionUseCaseFactory()


def build_weekly_report_service():
    return WeeklyReportService()


def build_prediction_trend_use_case():
    return prediction_use_cases.build_list_prediction_trend_use_case()


def _json_result(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@profile_bp.route("", methods=["GET"])
@token_required
def get_profile(current_user):
    """获取当前用户完整档案（账号+健康数据合并返回）"""
    return jsonify({"profile": current_user.to_dict()})


@profile_bp.route("/prediction-trend", methods=["GET"])
@token_required
def get_prediction_trend(current_user):
    limit = normalize_per_page(request.args.get("limit", 20, type=int), default=20)
    return jsonify(
        build_prediction_trend_use_case().execute(
            user_id=current_user.id,
            limit=limit,
        )
    )


@profile_bp.route("", methods=["PUT"])
@token_required
def update_profile(current_user):
    """
    更新个人健康档案。
    如果 user_profiles 表中没有对应行，自动创建。
    可更新字段：nickname, avatar, diagnosis, age, male, height, weight,
                current_smoker, cigs_per_day, bp_meds, diabetes, tot_chol, glucose
    BMI 由 height + weight 自动计算，无需传入。
    """
    data = request.get_json()
    return _json_result(profile_service.update_profile(current_user, data))
