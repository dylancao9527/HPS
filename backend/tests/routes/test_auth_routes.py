import time
from types import SimpleNamespace

import pytest
from flask import Flask

from routes import auth
from services import auth_service


def _app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="test-secret-key-for-jwt-hs256-tests",
        JWT_EXPIRATION_DAYS=7,
        ENABLE_LOCAL_MOCK_EMAIL_SERVICE=True,
    )
    return app


def _json_and_status(result):
    if isinstance(result, tuple):
        response, status = result
    else:
        response, status = result, 200
    return response.get_json(), status


class FakeField:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return ("eq", self.name, other)


class FakeQueryResult:
    def __init__(self, result):
        self.result = result

    def first(self):
        return self.result


class FakeUserQuery:
    def __init__(self, *, filter_by_results=None, filter_result=None):
        self.filter_by_results = filter_by_results or {}
        self.filter_result = filter_result
        self.filter_by_calls = []
        self.filter_calls = []

    def filter_by(self, **kwargs):
        self.filter_by_calls.append(kwargs)
        key = tuple(sorted(kwargs.items()))
        return FakeQueryResult(self.filter_by_results.get(key))

    def filter(self, *args):
        self.filter_calls.append(args)
        return FakeQueryResult(self.filter_result)


class FakeUser:
    username = FakeField("username")
    email = FakeField("email")
    query = FakeUserQuery()
    next_id = 101

    def __init__(self, user_id=None, username="user", email="user@example.com"):
        self.id = user_id if user_id is not None else FakeUser.next_id
        self.username = username
        self.email = email
        self.password_hash = None
        self.passwords = []
        self.valid_password = True
        self.role = "user"

    @property
    def is_admin(self):
        return self.role == "admin"

    def set_password(self, password):
        self.passwords.append(password)
        self.password_hash = f"hashed:{password}"

    def check_password(self, password):
        return self.valid_password and password == "Correct123!"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": "user",
        }


class FakeAdminUser(FakeUser):
    username = FakeField("username")
    email = FakeField("email")
    query = FakeUserQuery()

    @property
    def is_admin(self):
        return True

    def to_dict(self):
        return {
            "id": f"admin:{self.id}",
            "username": self.username,
            "email": self.email,
            "role": "admin",
        }


class FakeSession:
    def __init__(self):
        self.added = []
        self.commits = 0

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.commits += 1


def _install_user_query(monkeypatch, query):
    monkeypatch.setattr(auth_service, "User", FakeUser)
    FakeUser.query = query


def _install_admin_query(monkeypatch, query):
    monkeypatch.setattr(auth_service, "AdminUser", FakeAdminUser)
    FakeAdminUser.query = query


@pytest.fixture(autouse=True)
def isolate_auth_test_state(monkeypatch):
    auth._reset_codes.clear()
    auth.email_code_service.random_int = auth.email_code_service.__class__().random_int
    auth.email_code_service.time_provider = time.time
    _install_admin_query(monkeypatch, FakeUserQuery())
    monkeypatch.setattr(auth_service, "store_email", lambda **kwargs: None)


def test_validate_password_strength_and_email_format():
    assert auth.validate_password_strength("") == "密码不能为空"
    assert auth.validate_password_strength("short1!") == "密码长度需在 8~32 位之间"
    assert auth.validate_password_strength("abcdefgh") == "密码需至少包含字母、数字、符号中的两种"
    assert auth.validate_password_strength("Password1") is None

    assert auth.validate_email_format("") == "请输入邮箱"
    assert auth.validate_email_format("bad-email") == "邮箱格式不正确"
    assert auth.validate_email_format("user@example.com") is None


def test_email_code_generation_and_verify(monkeypatch):
    auth.email_code_service.random_int = lambda start, end: 123456

    assert auth._generate_email_code("key") == "123456"
    assert auth._verify_email_code("key", "000000") == "验证码错误"
    assert auth._verify_email_code("key", "123456") is None


def test_email_code_verify_missing_and_expired(monkeypatch):
    assert auth._verify_email_code("missing", "123456") == "请先获取验证码"

    auth._reset_codes["expired"] = {"code": "123456", "expires": time.time() - 1}
    assert auth._verify_email_code("expired", "123456") == "验证码已过期，请重新获取"
    assert "expired" not in auth._reset_codes


def test_send_register_code_validates_email(monkeypatch):
    app = _app()
    _install_user_query(monkeypatch, FakeUserQuery())

    with app.test_request_context("/api/auth/send-register-code", method="POST", json={}):
        payload, status = _json_and_status(auth.send_register_code())
    assert status == 400
    assert payload == {"error": "请输入邮箱"}

    with app.test_request_context(
        "/api/auth/send-register-code",
        method="POST",
        json={"email": "bad-email"},
    ):
        payload, status = _json_and_status(auth.send_register_code())
    assert status == 400
    assert payload == {"error": "邮箱格式不正确"}


def test_send_register_code_rejects_existing_email(monkeypatch):
    app = _app()
    _install_user_query(
        monkeypatch,
        FakeUserQuery(
            filter_by_results={
                (("email", "taken@example.com"),): FakeUser(
                    user_id=7,
                    email="taken@example.com",
                )
            }
        ),
    )

    with app.test_request_context(
        "/api/auth/send-register-code",
        method="POST",
        json={"email": "taken@example.com"},
    ):
        payload, status = _json_and_status(auth.send_register_code())

    assert status == 409
    assert payload == {"error": "该邮箱已被注册"}


def test_send_register_code_success_uses_mock_message(monkeypatch):
    app = _app()
    _install_user_query(monkeypatch, FakeUserQuery())
    monkeypatch.setattr(auth.email_code_service, "generate_code", lambda cache_key: "123456")

    with app.test_request_context(
        "/api/auth/send-register-code",
        method="POST",
        json={"email": "new@example.com"},
    ):
        payload, status = _json_and_status(auth.send_register_code())

    assert status == 200
    assert payload == {
        "message": "验证码已发送，请在本地模拟邮箱中查看",
        "mock_service": "local_email",
        "expires_in_seconds": 300,
        "resend_after_seconds": 60,
    }


def test_register_rejects_missing_weak_and_bad_code(monkeypatch):
    app = _app()
    _install_user_query(monkeypatch, FakeUserQuery())

    with app.test_request_context("/api/auth/register", method="POST", json={}):
        payload, status = _json_and_status(auth.register())
    assert status == 400
    assert payload == {"error": "请填写所有字段"}

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={
            "username": "alice",
            "password": "weak",
            "email": "alice@example.com",
            "code": "123456",
        },
    ):
        payload, status = _json_and_status(auth.register())
    assert status == 400
    assert payload == {"error": "密码长度需在 8~32 位之间"}

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={
            "username": "alice",
            "password": "Password1",
            "email": "alice@example.com",
            "code": "123456",
        },
    ):
        payload, status = _json_and_status(auth.register())
    assert status == 400
    assert payload == {"error": "请先获取验证码"}


def test_register_rejects_duplicate_email_or_username(monkeypatch):
    app = _app()
    duplicate_email = FakeUser(user_id=1, email="alice@example.com")
    duplicate_name = FakeUser(user_id=2, username="alice")
    _install_user_query(
        monkeypatch,
        FakeUserQuery(
            filter_by_results={
                (("email", "alice@example.com"),): duplicate_email,
                (("username", "alice"),): duplicate_name,
            }
        ),
    )
    auth._reset_codes["reg_alice@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={
            "username": "alice",
            "password": "Password1",
            "email": "alice@example.com",
            "code": "123456",
        },
    ):
        payload, status = _json_and_status(auth.register())
    assert status == 409
    assert payload == {"error": "该邮箱已被注册"}

    _install_user_query(
        monkeypatch,
        FakeUserQuery(
            filter_by_results={
                (("email", "alice@example.com"),): None,
                (("username", "alice"),): duplicate_name,
            }
        ),
    )
    auth._reset_codes["reg_alice@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={
            "username": "alice",
            "password": "Password1",
            "email": "alice@example.com",
            "code": "123456",
        },
    ):
        payload, status = _json_and_status(auth.register())
    assert status == 409
    assert payload == {"error": "用户名已存在"}


def test_register_success_creates_user_and_returns_token(monkeypatch):
    app = _app()
    fake_session = FakeSession()
    _install_user_query(monkeypatch, FakeUserQuery())
    monkeypatch.setattr(auth_service.db, "session", fake_session, raising=False)
    auth._reset_codes["reg_alice@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }

    with app.test_request_context(
        "/api/auth/register",
        method="POST",
        json={
            "username": "alice",
            "password": "Password1",
            "email": "alice@example.com",
            "code": "123456",
        },
    ):
        payload, status = _json_and_status(auth.register())

    assert status == 201
    assert payload["message"] == "注册成功"
    assert payload["token"]
    assert payload["user"] == {
        "id": 101,
        "username": "alice",
        "email": "alice@example.com",
        "role": "user",
    }
    assert fake_session.added[0].username == "alice"
    assert fake_session.added[0].email == "alice@example.com"
    assert fake_session.commits == 1
    assert "reg_alice@example.com" not in auth._reset_codes


def test_auth_routes_no_longer_expose_ambiguous_login_entry():
    assert not hasattr(auth, "login")


def test_user_login_route_rejects_invalid_credentials_and_returns_token(monkeypatch):
    app = _app()
    user = FakeUser(user_id=7, username="alice", email="alice@example.com")
    _install_user_query(monkeypatch, FakeUserQuery(filter_result=None))
    monkeypatch.setattr(auth_service, "or_", lambda *args: ("or", args))

    with app.test_request_context(
        "/api/auth/login/user",
        method="POST",
        json={"username": "alice", "password": "bad"},
    ):
        payload, status = _json_and_status(auth.user_login())
    assert status == 401
    assert payload == {"error": "用户名、邮箱或密码错误"}

    _install_user_query(monkeypatch, FakeUserQuery(filter_result=user))
    with app.test_request_context(
        "/api/auth/login/user",
        method="POST",
        json={"username": "alice", "password": "Correct123!"},
    ):
        payload, status = _json_and_status(auth.user_login())
    assert status == 200
    assert payload["message"] == "登录成功"
    assert payload["token"]
    assert payload["user"] == {
        "id": 7,
        "username": "alice",
        "email": "alice@example.com",
        "role": "user",
    }


def test_user_login_route_rejects_admin_account(monkeypatch):
    app = _app()
    admin_user = FakeAdminUser(user_id=8, username="root", email="root@example.com")
    _install_user_query(monkeypatch, FakeUserQuery(filter_result=None))
    _install_admin_query(monkeypatch, FakeUserQuery(filter_result=admin_user))
    monkeypatch.setattr(auth_service, "or_", lambda *args: ("or", args))

    with app.test_request_context(
        "/api/auth/login/user",
        method="POST",
        json={"username": "root", "password": "Correct123!"},
    ):
        payload, status = _json_and_status(auth.user_login())

    assert status == 403
    assert payload == {"error": "请使用管理员登录入口"}


def test_admin_login_route_accepts_admin_without_backend_captcha(monkeypatch):
    app = _app()
    admin_user = FakeAdminUser(user_id=8, username="root", email="root@example.com")
    _install_user_query(monkeypatch, FakeUserQuery(filter_result=None))
    _install_admin_query(monkeypatch, FakeUserQuery(filter_result=admin_user))
    monkeypatch.setattr(auth_service, "or_", lambda *args: ("or", args))

    with app.test_request_context(
        "/api/auth/login/admin",
        method="POST",
        json={"username": "root", "password": "Correct123!"},
    ):
        payload, status = _json_and_status(auth.admin_login())

    assert status == 200
    assert payload["message"] == "登录成功"
    assert payload["token"]
    assert payload["user"] == {
        "id": "admin:8",
        "username": "root",
        "email": "root@example.com",
        "role": "admin",
    }


def test_admin_login_route_rejects_user_account(monkeypatch):
    app = _app()
    user = FakeUser(user_id=9, username="alice", email="alice@example.com")
    _install_user_query(monkeypatch, FakeUserQuery(filter_result=user))
    monkeypatch.setattr(auth_service, "or_", lambda *args: ("or", args))

    with app.test_request_context(
        "/api/auth/login/admin",
        method="POST",
        json={"username": "alice", "password": "Correct123!"},
    ):
        payload, status = _json_and_status(auth.admin_login())

    assert status == 403
    assert payload == {"error": "该账号不是管理员账号"}


def test_change_password_contract(monkeypatch):
    app = _app()
    fake_session = FakeSession()
    user = FakeUser(user_id=7)
    monkeypatch.setattr(auth_service.db, "session", fake_session, raising=False)

    with app.test_request_context("/api/auth/change-password", method="POST", json={}):
        payload, status = _json_and_status(auth.change_password.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "请填写旧密码和新密码"}

    with app.test_request_context(
        "/api/auth/change-password",
        method="POST",
        json={"old_password": "bad", "new_password": "Password1"},
    ):
        payload, status = _json_and_status(auth.change_password.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "旧密码错误"}

    with app.test_request_context(
        "/api/auth/change-password",
        method="POST",
        json={"old_password": "Correct123!", "new_password": "weak"},
    ):
        payload, status = _json_and_status(auth.change_password.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "密码长度需在 8~32 位之间"}

    with app.test_request_context(
        "/api/auth/change-password",
        method="POST",
        json={"old_password": "Correct123!", "new_password": "Correct123!"},
    ):
        payload, status = _json_and_status(auth.change_password.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "新密码不能与旧密码相同"}

    with app.test_request_context(
        "/api/auth/change-password",
        method="POST",
        json={"old_password": "Correct123!", "new_password": "Newpass123!"},
    ):
        payload, status = _json_and_status(auth.change_password.__wrapped__(user))
    assert status == 200
    assert payload == {"message": "密码修改成功"}
    assert user.passwords == ["Newpass123!"]
    assert fake_session.commits == 1


def test_send_change_email_code_contract(monkeypatch):
    app = _app()
    user = FakeUser(user_id=7, email="old@example.com")
    _install_user_query(monkeypatch, FakeUserQuery())
    monkeypatch.setattr(auth.email_code_service, "generate_code", lambda cache_key: "123456")

    with app.test_request_context(
        "/api/auth/send-change-email-code",
        method="POST",
        json={"email": "bad-email"},
    ):
        payload, status = _json_and_status(auth.send_change_email_code.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "邮箱格式不正确"}

    with app.test_request_context(
        "/api/auth/send-change-email-code",
        method="POST",
        json={"email": "old@example.com"},
    ):
        payload, status = _json_and_status(auth.send_change_email_code.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "新邮箱不能与当前邮箱相同"}

    _install_user_query(
        monkeypatch,
        FakeUserQuery(
            filter_by_results={
                (("email", "taken@example.com"),): FakeUser(email="taken@example.com")
            }
        ),
    )
    with app.test_request_context(
        "/api/auth/send-change-email-code",
        method="POST",
        json={"email": "taken@example.com"},
    ):
        payload, status = _json_and_status(auth.send_change_email_code.__wrapped__(user))
    assert status == 409
    assert payload == {"error": "该邮箱已被注册"}

    _install_user_query(monkeypatch, FakeUserQuery())
    with app.test_request_context(
        "/api/auth/send-change-email-code",
        method="POST",
        json={"email": "new@example.com"},
    ):
        payload, status = _json_and_status(auth.send_change_email_code.__wrapped__(user))
    assert status == 200
    assert payload == {
        "message": "验证码已发送，请在本地模拟邮箱中查看",
        "mock_service": "local_email",
        "expires_in_seconds": 300,
        "resend_after_seconds": 60,
    }


def test_update_account_contract(monkeypatch):
    app = _app()
    user = FakeUser(user_id=7, username="alice", email="old@example.com")
    fake_session = FakeSession()
    monkeypatch.setattr(auth_service.db, "session", fake_session, raising=False)
    monkeypatch.setattr(auth_service, "User", FakeUser)

    with app.test_request_context("/api/auth/update-account", method="POST", json={}):
        payload, status = _json_and_status(auth.update_account.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "用户名不能为空"}

    FakeUser.query = FakeUserQuery(
        filter_by_results={(("username", "bob"),): FakeUser(user_id=8, username="bob")}
    )
    with app.test_request_context(
        "/api/auth/update-account",
        method="POST",
        json={"username": "bob"},
    ):
        payload, status = _json_and_status(auth.update_account.__wrapped__(user))
    assert status == 409
    assert payload == {"error": "用户名已存在"}

    FakeUser.query = FakeUserQuery()
    with app.test_request_context(
        "/api/auth/update-account",
        method="POST",
        json={"username": "alice", "email": "new@example.com"},
    ):
        payload, status = _json_and_status(auth.update_account.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "修改邮箱需要验证码"}

    auth._reset_codes["change_email:7:new@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }
    with app.test_request_context(
        "/api/auth/update-account",
        method="POST",
        json={"username": "alice2", "email": "new@example.com", "email_code": "bad"},
    ):
        payload, status = _json_and_status(auth.update_account.__wrapped__(user))
    assert status == 400
    assert payload == {"error": "验证码错误"}

    auth._reset_codes["change_email:7:new@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }
    with app.test_request_context(
        "/api/auth/update-account",
        method="POST",
        json={
            "username": "alice2",
            "email": "new@example.com",
            "email_code": "123456",
        },
    ):
        payload, status = _json_and_status(auth.update_account.__wrapped__(user))
    assert status == 200
    assert payload == {
        "message": "账号信息已更新",
        "user": {
            "id": 7,
            "username": "alice2",
            "email": "new@example.com",
            "role": "user",
        },
    }
    assert fake_session.commits == 1
    assert "change_email:7:new@example.com" not in auth._reset_codes


def test_forgot_and_reset_password_contract(monkeypatch):
    app = _app()
    user = FakeUser(user_id=7, email="alice@example.com")
    fake_session = FakeSession()
    monkeypatch.setattr(auth_service.db, "session", fake_session, raising=False)
    monkeypatch.setattr(auth_service, "User", FakeUser)

    with app.test_request_context("/api/auth/forgot-password", method="POST", json={}):
        payload, status = _json_and_status(auth.forgot_password())
    assert status == 400
    assert payload == {"error": "请输入邮箱"}

    FakeUser.query = FakeUserQuery()
    with app.test_request_context(
        "/api/auth/forgot-password",
        method="POST",
        json={"email": "missing@example.com"},
    ):
        payload, status = _json_and_status(auth.forgot_password())
    assert status == 404
    assert payload == {"error": "该邮箱未注册"}

    FakeUser.query = FakeUserQuery(
        filter_by_results={(("email", "alice@example.com"),): user}
    )
    monkeypatch.setattr(auth.email_code_service, "generate_code", lambda cache_key: "123456")
    with app.test_request_context(
        "/api/auth/forgot-password",
        method="POST",
        json={"email": "alice@example.com"},
    ):
        payload, status = _json_and_status(auth.forgot_password())
    assert status == 200
    assert payload == {
        "message": "验证码已发送，请在本地模拟邮箱中查看",
        "mock_service": "local_email",
        "expires_in_seconds": 300,
        "resend_after_seconds": 60,
    }

    with app.test_request_context("/api/auth/reset-password", method="POST", json={}):
        payload, status = _json_and_status(auth.reset_password())
    assert status == 400
    assert payload == {"error": "请填写所有字段"}

    with app.test_request_context(
        "/api/auth/reset-password",
        method="POST",
        json={
            "email": "alice@example.com",
            "code": "bad",
            "new_password": "Password1",
        },
    ):
        payload, status = _json_and_status(auth.reset_password())
    assert status == 400
    assert payload == {"error": "请先获取验证码"}

    auth._reset_codes["alice@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }
    FakeUser.query = FakeUserQuery()
    with app.test_request_context(
        "/api/auth/reset-password",
        method="POST",
        json={
            "email": "alice@example.com",
            "code": "123456",
            "new_password": "Password1",
        },
    ):
        payload, status = _json_and_status(auth.reset_password())
    assert status == 404
    assert payload == {"error": "用户不存在"}

    auth._reset_codes["alice@example.com"] = {
        "code": "123456",
        "expires": time.time() + 300,
    }
    FakeUser.query = FakeUserQuery(
        filter_by_results={(("email", "alice@example.com"),): user}
    )
    with app.test_request_context(
        "/api/auth/reset-password",
        method="POST",
        json={
            "email": "alice@example.com",
            "code": "123456",
            "new_password": "Password1",
        },
    ):
        payload, status = _json_and_status(auth.reset_password())
    assert status == 200
    assert payload == {"message": "密码重置成功，请使用新密码登录"}
    assert user.passwords == ["Password1"]
    assert fake_session.commits == 1
    assert "alice@example.com" not in auth._reset_codes
