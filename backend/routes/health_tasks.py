from flask import Blueprint, jsonify

from routes.auth import token_required
from services.health_task_service import HealthTaskService

health_tasks_bp = Blueprint("health_tasks", __name__, url_prefix="/api/health-tasks")


def build_health_task_service():
    return HealthTaskService()


@health_tasks_bp.route("/today", methods=["GET"])
@token_required
def get_today_health_tasks(current_user):
    summary = build_health_task_service().get_today_summary(current_user.id)
    return jsonify(summary)
