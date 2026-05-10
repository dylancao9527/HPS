import math
import secrets
import time

from flask import current_app
from sqlalchemy import or_

from extensions import db
from models import AdminUser, User
from services.account_contract import validate_email_format, validate_password_strength
from services.mock_email_service import store_email


def _secure_random_int(start, end):
    return start + secrets.randbelow(end - start + 1)


class EmailCodeService:
    def __init__(
        self,
        *,
        code_store=None,
        code_ttl_seconds=300,
        resend_cooldown_seconds=60,
        max_verify_attempts=5,
        random_int=None,
        time_provider=time.time,
    ):
        self.code_store = code_store if code_store is not None else {}
        self.code_ttl_seconds = code_ttl_seconds
        self.resend_cooldown_seconds = resend_cooldown_seconds
        self.max_verify_attempts = max_verify_attempts
        self.random_int = random_int or _secure_random_int
        self.time_provider = time_provider

    def generate_code(self, cache_key):
        code = str(self.random_int(100000, 999999))
        now = self.time_provider()
        self.code_store[cache_key] = {
            "code": code,
            "expires": now + self.code_ttl_seconds,
            "sent_at": now,
            "failed_attempts": 0,
        }
        return code

    def issue_code(self, cache_key, *, email, scene):
        cached = self.code_store.get(cache_key)
        if cached and self.time_provider() <= cached.get("expires", 0):
            retry_after = self._retry_after_seconds(cached)
            if retry_after > 0:
                return (
                    {
                        "error": f"验证码已发送，请 {retry_after} 秒后再重新获取",
                        "retry_after_seconds": retry_after,
                    },
                    429,
                )

        code = self.generate_code(cache_key)
        if cache_key in self.code_store:
            self.code_store[cache_key].update({"scene": scene, "email": email})
        self.deliver_local_mock_email(email=email, scene=scene, code=code)
        return self.response_message()

    def _retry_after_seconds(self, cached):
        sent_at = cached.get("sent_at")
        if sent_at is None:
            return 0
        retry_at = sent_at + self.resend_cooldown_seconds
        return max(0, math.ceil(retry_at - self.time_provider()))

    def verify_code(self, cache_key, code):
        cached = self.code_store.get(cache_key)
        if not cached:
            return "请先获取验证码"
        if self.time_provider() > cached["expires"]:
            del self.code_store[cache_key]
            return "验证码已过期，请重新获取"
        if cached["code"] != code:
            failed_attempts = int(cached.get("failed_attempts", 0)) + 1
            if failed_attempts >= self.max_verify_attempts:
                del self.code_store[cache_key]
                return "验证码错误次数过多，请重新获取"
            cached["failed_attempts"] = failed_attempts
            return "验证码错误"
        return None

    def remove_code(self, cache_key):
        self.code_store.pop(cache_key, None)

    def mock_email_enabled(self):
        return current_app.config.get("ENABLE_LOCAL_MOCK_EMAIL_SERVICE", False)

    def deliver_local_mock_email(self, *, email, scene, code):
        if not self.mock_email_enabled():
            return

        scene_title = {
            "register": "注册",
            "change_email": "修改邮箱",
            "reset_password": "重置密码",
        }
        store_email(
            recipient=email,
            scene=scene,
            code=code,
            subject=f"Hypertension Prediction - {scene_title.get(scene, '验证码')}",
            body=(
                f"本地模拟邮箱服务已生成用于{scene_title.get(scene, '验证')}的验证码。\n"
                f"验证码：{code}\n"
                "该邮件仅用于本地开发与实验验证，不会真正发送到外部邮箱。"
            ),
        )

    def response_message(self):
        if self.mock_email_enabled():
            return {
                "message": "验证码已发送，请在本地模拟邮箱中查看",
                "mock_service": "local_email",
                "expires_in_seconds": self.code_ttl_seconds,
                "resend_after_seconds": self.resend_cooldown_seconds,
            }
        return {
            "message": "验证码已发送",
            "expires_in_seconds": self.code_ttl_seconds,
            "resend_after_seconds": self.resend_cooldown_seconds,
        }


class RegistrationService:
    def __init__(self, *, email_code_service, token_generator):
        self.email_code_service = email_code_service
        self.token_generator = token_generator

    def send_register_code(self, data):
        email = data.get("email", "").strip()

        if not email:
            return {"error": "请输入邮箱"}, 400

        email_error = validate_email_format(email)
        if email_error:
            return {"error": email_error}, 400

        if User.query.filter_by(email=email).first() or AdminUser.query.filter_by(
            email=email
        ).first():
            return {"error": "该邮箱已被注册"}, 409

        return self.email_code_service.issue_code(
            f"reg_{email}",
            email=email,
            scene="register",
        )

    def register(self, data):
        username = data.get("username", "").strip()
        password = data.get("password", "")
        email = data.get("email", "").strip()
        code = data.get("code", "").strip()

        if not all([username, password, email, code]):
            return {"error": "请填写所有字段"}, 400

        password_error = validate_password_strength(password)
        if password_error:
            return {"error": password_error}, 400

        email_error = validate_email_format(email)
        if email_error:
            return {"error": email_error}, 400

        code_error = self.email_code_service.verify_code(f"reg_{email}", code)
        if code_error:
            return {"error": code_error}, 400

        if User.query.filter_by(email=email).first() or AdminUser.query.filter_by(
            email=email
        ).first():
            return {"error": "该邮箱已被注册"}, 409
        if User.query.filter_by(username=username).first() or AdminUser.query.filter_by(
            username=username
        ).first():
            return {"error": "用户名已存在"}, 409

        user = User()
        user.username = username
        user.email = email
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        self.email_code_service.remove_code(f"reg_{email}")
        return (
            {
                "message": "注册成功",
                "token": self.token_generator(user.id, account_type="user"),
                "user": user.to_dict(),
            },
            201,
        )


class LoginService:
    def __init__(self, *, token_generator):
        self.token_generator = token_generator

    def login(self, data, *, required_role=None):
        login_id = data.get("username", "").strip()
        password = data.get("password", "")
        login_role = required_role or data.get("login_role", "").strip() or "user"

        if login_role == "admin":
            admin = self._find_admin(login_id)
            if admin and admin.check_password(password):
                return {
                    "message": "登录成功",
                    "token": self.token_generator(admin.id, account_type="admin"),
                    "user": admin.to_dict(),
                }

            user = self._find_user(login_id)
            if user and user.check_password(password):
                return {"error": "该账号不是管理员账号"}, 403

            return {"error": "用户名、邮箱或密码错误"}, 401

        user = self._find_user(login_id)

        if user and user.check_password(password):
            return {
                "message": "登录成功",
                "token": self.token_generator(user.id, account_type="user"),
                "user": user.to_dict(),
            }

        admin = self._find_admin(login_id)
        if admin and admin.check_password(password):
            return {"error": "请使用管理员登录入口"}, 403

        return {"error": "用户名、邮箱或密码错误"}, 401

    def _find_user(self, login_id):
        return User.query.filter(
            or_(User.username == login_id, User.email == login_id)
        ).first()

    def _find_admin(self, login_id):
        return AdminUser.query.filter(
            or_(AdminUser.username == login_id, AdminUser.email == login_id)
        ).first()


class AccountMaintenanceService:
    def __init__(self, *, email_code_service):
        self.email_code_service = email_code_service

    def change_password(self, current_user, data):
        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")

        if not old_password or not new_password:
            return {"error": "请填写旧密码和新密码"}, 400

        if not current_user.check_password(old_password):
            return {"error": "旧密码错误"}, 400

        password_error = validate_password_strength(new_password)
        if password_error:
            return {"error": password_error}, 400

        if old_password == new_password:
            return {"error": "新密码不能与旧密码相同"}, 400

        current_user.set_password(new_password)
        db.session.commit()

        return {"message": "密码修改成功"}

    def send_change_email_code(self, current_user, data):
        new_email = data.get("email", "").strip()

        email_error = validate_email_format(new_email)
        if email_error:
            return {"error": email_error}, 400
        if new_email == current_user.email:
            return {"error": "新邮箱不能与当前邮箱相同"}, 400
        if User.query.filter_by(email=new_email).first() or AdminUser.query.filter_by(
            email=new_email
        ).first():
            return {"error": "该邮箱已被注册"}, 409

        cache_key = f"change_email:{current_user.id}:{new_email}"
        return self.email_code_service.issue_code(
            cache_key,
            email=new_email,
            scene="change_email",
        )

    def update_account(self, current_user, data):
        username = data.get("username", "").strip()
        new_email = data.get("email", "").strip()
        email_code = data.get("email_code", "").strip()

        if not username:
            return {"error": "用户名不能为空"}, 400

        if username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            existing_admin_user = AdminUser.query.filter_by(username=username).first()
            if existing_user and existing_user.id != current_user.id:
                return {"error": "用户名已存在"}, 409
            if existing_admin_user:
                return {"error": "用户名已存在"}, 409
            current_user.username = username

        if new_email:
            email_error = validate_email_format(new_email)
            if email_error:
                return {"error": email_error}, 400

            if new_email != current_user.email:
                existing_email_user = User.query.filter_by(email=new_email).first()
                existing_admin_email = AdminUser.query.filter_by(email=new_email).first()
                if existing_email_user and existing_email_user.id != current_user.id:
                    return {"error": "该邮箱已被注册"}, 409
                if existing_admin_email:
                    return {"error": "该邮箱已被注册"}, 409

                if not email_code:
                    return {"error": "修改邮箱需要验证码"}, 400

                cache_key = f"change_email:{current_user.id}:{new_email}"
                code_error = self.email_code_service.verify_code(cache_key, email_code)
                if code_error:
                    return {"error": code_error}, 400

                current_user.email = new_email
                self.email_code_service.remove_code(cache_key)

        db.session.commit()
        return {"message": "账号信息已更新", "user": current_user.to_dict()}


class PasswordResetService:
    def __init__(self, *, email_code_service):
        self.email_code_service = email_code_service

    def forgot_password(self, data):
        email = data.get("email", "").strip()

        if not email:
            return {"error": "请输入邮箱"}, 400

        email_error = validate_email_format(email)
        if email_error:
            return {"error": email_error}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"error": "该邮箱未注册"}, 404

        return self.email_code_service.issue_code(
            email,
            email=email,
            scene="reset_password",
        )

    def reset_password(self, data):
        email = data.get("email", "").strip()
        code = data.get("code", "").strip()
        new_password = data.get("new_password", "")

        if not all([email, code, new_password]):
            return {"error": "请填写所有字段"}, 400

        email_error = validate_email_format(email)
        if email_error:
            return {"error": email_error}, 400

        password_error = validate_password_strength(new_password)
        if password_error:
            return {"error": password_error}, 400

        code_error = self.email_code_service.verify_code(email, code)
        if code_error:
            return {"error": code_error}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"error": "用户不存在"}, 404

        user.set_password(new_password)
        db.session.commit()

        self.email_code_service.remove_code(email)
        return {"message": "密码重置成功，请使用新密码登录"}


class AuthAccountService:
    def __init__(self, *, email_code_service, token_generator):
        self.registration_service = RegistrationService(
            email_code_service=email_code_service,
            token_generator=token_generator,
        )
        self.login_service = LoginService(token_generator=token_generator)
        self.account_maintenance_service = AccountMaintenanceService(
            email_code_service=email_code_service,
        )
        self.password_reset_service = PasswordResetService(
            email_code_service=email_code_service,
        )

    def send_register_code(self, data):
        return self.registration_service.send_register_code(data)

    def register(self, data):
        return self.registration_service.register(data)

    def login(self, data, *, required_role=None):
        return self.login_service.login(data, required_role=required_role)

    def change_password(self, current_user, data):
        return self.account_maintenance_service.change_password(current_user, data)

    def send_change_email_code(self, current_user, data):
        return self.account_maintenance_service.send_change_email_code(
            current_user,
            data,
        )

    def update_account(self, current_user, data):
        return self.account_maintenance_service.update_account(current_user, data)

    def forgot_password(self, data):
        return self.password_reset_service.forgot_password(data)

    def reset_password(self, data):
        return self.password_reset_service.reset_password(data)
