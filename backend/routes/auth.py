from datetime import timedelta
from functools import wraps

import jwt
from flask import Blueprint, current_app, jsonify, request

from extensions import db
from models import AdminUser, User
from services.auth_service import (
    AuthAccountService,
    EmailCodeService,
    validate_email_format,
    validate_password_strength,
)
from utils.time_utils import utc_now

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

_reset_codes = {}
email_code_service = EmailCodeService(code_store=_reset_codes)


def generate_token(account_id, *, account_type="user"):
    days = current_app.config.get("JWT_EXPIRATION_DAYS", 7)
    now = utc_now()
    payload = {
        "user_id": account_id,
        "account_type": account_type,
        "exp": now + timedelta(days=days),
        "iat": now,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "未登录，请先登录"}), 401

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            account_type = payload.get("account_type", "user")
            account_model = AdminUser if account_type == "admin" else User
            current_user = db.session.get(account_model, payload["user_id"])
            if not current_user:
                return jsonify({"error": "用户不存在"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token 已过期，请重新登录"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "无效的 Token"}), 401
        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({"error": "需要管理员权限"}), 403
        return f(current_user, *args, **kwargs)

    return decorated


def _generate_email_code(cache_key):
    return email_code_service.generate_code(cache_key)


def _verify_email_code(cache_key, code):
    return email_code_service.verify_code(cache_key, code)


def _mock_email_enabled():
    return email_code_service.mock_email_enabled()


def _deliver_local_mock_email(*, email, scene, code):
    email_code_service.deliver_local_mock_email(email=email, scene=scene, code=code)


def _mock_response_message():
    return email_code_service.response_message()


auth_account_service = AuthAccountService(
    email_code_service=email_code_service,
    token_generator=generate_token,
)


def _json_result(result):
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@auth_bp.route("/send-register-code", methods=["POST"])
def send_register_code():
    data = request.get_json() or {}
    return _json_result(auth_account_service.send_register_code(data))


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    return _json_result(auth_account_service.register(data))


@auth_bp.route("/login/user", methods=["POST"])
def user_login():
    data = request.get_json() or {}
    return _json_result(auth_account_service.login(data, required_role="user"))


@auth_bp.route("/login/admin", methods=["POST"])
def admin_login():
    data = request.get_json() or {}
    return _json_result(auth_account_service.login(data, required_role="admin"))


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me(current_user):
    return jsonify({"user": current_user.to_dict()})


@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    data = request.get_json() or {}
    return _json_result(auth_account_service.change_password(current_user, data))


@auth_bp.route("/send-change-email-code", methods=["POST"])
@token_required
def send_change_email_code(current_user):
    data = request.get_json() or {}
    return _json_result(auth_account_service.send_change_email_code(current_user, data))


@auth_bp.route("/update-account", methods=["POST"])
@token_required
def update_account(current_user):
    data = request.get_json() or {}
    return _json_result(auth_account_service.update_account(current_user, data))


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    return _json_result(auth_account_service.forgot_password(data))


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    return _json_result(auth_account_service.reset_password(data))
