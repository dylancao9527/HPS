from app import create_app


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
