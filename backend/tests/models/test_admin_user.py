from models.admin_user import AdminUser


def test_admin_user_dict_contains_account_fields_only():
    admin = AdminUser(id=1, username="root", email="root@example.com")

    payload = admin.to_dict()

    assert payload["id"] == "admin:1"
    assert payload["username"] == "root"
    assert payload["email"] == "root@example.com"
    assert payload["role"] == "admin"
    assert "age" not in payload
    assert "bmi" not in payload
    assert "profile_complete" not in payload
