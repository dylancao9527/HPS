from ipaddress import ip_address
from secrets import compare_digest

from flask import Blueprint, current_app, jsonify, request

from services.mock_email_service import get_latest_email


dev_tools_bp = Blueprint("dev_tools", __name__, url_prefix="/api/dev")


@dev_tools_bp.route("/mock-emails/latest", methods=["GET"])
def get_latest_mock_email():
    if not _can_read_mock_email():
        return jsonify({"error": "本地模拟邮箱接口仅允许本机访问或使用开发访问令牌"}), 403

    email = request.args.get("email", "").strip()
    scene = request.args.get("scene", "").strip() or None
    message = get_latest_email(recipient=email, scene=scene)
    return jsonify({"message": _sanitize_mock_email(message)})


def _can_read_mock_email():
    access_token = current_app.config.get("LOCAL_MOCK_EMAIL_ACCESS_TOKEN", "")
    if access_token:
        provided_token = request.headers.get("X-Dev-Tools-Token", "")
        return compare_digest(provided_token, access_token)
    return _request_from_loopback()


def _request_from_loopback():
    remote_addr = request.remote_addr or ""
    try:
        return ip_address(remote_addr).is_loopback
    except ValueError:
        return remote_addr == "localhost"


def _sanitize_mock_email(message):
    if not message:
        return None

    return {
        "email": message.get("email") or message.get("recipient"),
        "scene": message.get("scene"),
        "code": message.get("code"),
        "created_at": message.get("created_at"),
    }
