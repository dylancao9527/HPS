from app import create_app
from routes import dev_tools


def _rule_strings(flask_app):
    return {rule.rule for rule in flask_app.url_map.iter_rules()}


def test_create_app_skips_mock_email_route_when_local_mock_service_disabled():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "INIT_ADMIN_ON_STARTUP": False,
            "ENABLE_LOCAL_MOCK_EMAIL_SERVICE": False,
        }
    )

    assert "/api/dev/mock-emails/latest" not in _rule_strings(app)


def test_create_app_registers_mock_email_route_when_local_mock_service_enabled():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "INIT_ADMIN_ON_STARTUP": False,
            "ENABLE_LOCAL_MOCK_EMAIL_SERVICE": True,
        }
    )

    assert "/api/dev/mock-emails/latest" in _rule_strings(app)


def test_mock_email_route_rejects_non_local_requests_when_no_dev_token(monkeypatch):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "INIT_ADMIN_ON_STARTUP": False,
            "ENABLE_LOCAL_MOCK_EMAIL_SERVICE": True,
            "LOCAL_MOCK_EMAIL_ACCESS_TOKEN": "",
        }
    )
    monkeypatch.setattr(dev_tools, "get_latest_email", lambda **kwargs: None)

    response = app.test_client().get(
        "/api/dev/mock-emails/latest?email=alice@example.com",
        environ_base={"REMOTE_ADDR": "203.0.113.10"},
    )

    assert response.status_code == 403


def test_mock_email_route_returns_only_sanitized_message_for_local_request(monkeypatch):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "INIT_ADMIN_ON_STARTUP": False,
            "ENABLE_LOCAL_MOCK_EMAIL_SERVICE": True,
            "LOCAL_MOCK_EMAIL_ACCESS_TOKEN": "",
        }
    )
    monkeypatch.setattr(
        dev_tools,
        "get_latest_email",
        lambda **kwargs: {
            "recipient": "alice@example.com",
            "scene": "register",
            "subject": "验证码",
            "body": "验证码：123456",
            "code": "123456",
            "created_at": "2026-05-11T09:30:00+00:00",
        },
    )

    response = app.test_client().get(
        "/api/dev/mock-emails/latest?email=alice@example.com&scene=register",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": {
            "email": "alice@example.com",
            "scene": "register",
            "code": "123456",
            "created_at": "2026-05-11T09:30:00+00:00",
        }
    }
