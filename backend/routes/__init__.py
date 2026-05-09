from .auth import auth_bp
from .profile import profile_bp
from .bp_records import bp_records_bp
from .predictions import predictions_bp
from .admin import admin_bp
from .dev_tools import dev_tools_bp
from .health_tasks import health_tasks_bp
from .weekly_report import weekly_report_bp

__all__ = [
    "auth_bp",
    "profile_bp",
    "bp_records_bp",
    "predictions_bp",
    "admin_bp",
    "dev_tools_bp",
    "health_tasks_bp",
    "weekly_report_bp",
]
