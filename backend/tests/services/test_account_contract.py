from services.account_contract import (
    count_password_character_classes,
    validate_email_format,
    validate_password_strength,
)


def test_account_contract_counts_backend_password_character_classes():
    assert count_password_character_classes("abcdefgh") == 1
    assert count_password_character_classes("Password") == 1
    assert count_password_character_classes("Password1") == 2
    assert count_password_character_classes("Password1!") == 3


def test_account_contract_validates_password_strength_messages():
    assert validate_password_strength("") == "密码不能为空"
    assert validate_password_strength("short1!") == "密码长度需在 8~32 位之间"
    assert (
        validate_password_strength("abcdefgh")
        == "密码需至少包含字母、数字、符号中的两种"
    )
    assert validate_password_strength("Password1") is None


def test_account_contract_validates_email_format_messages():
    assert validate_email_format("") == "请输入邮箱"
    assert validate_email_format("bad-email") == "邮箱格式不正确"
    assert validate_email_format("user@example.com") is None
