import re


EMAIL_PATTERN = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 32


def count_password_character_classes(password):
    classes = 0
    if re.search(r"[a-zA-Z]", password):
        classes += 1
    if re.search(r"\d", password):
        classes += 1
    if re.search(r"[^a-zA-Z\d]", password):
        classes += 1
    return classes


def validate_password_strength(password):
    if not password:
        return "密码不能为空"
    if len(password) < PASSWORD_MIN_LENGTH or len(password) > PASSWORD_MAX_LENGTH:
        return "密码长度需在 8~32 位之间"
    if count_password_character_classes(password) < 2:
        return "密码需至少包含字母、数字、符号中的两种"
    return None


def validate_email_format(email):
    if not email:
        return "请输入邮箱"
    if not re.match(EMAIL_PATTERN, email):
        return "邮箱格式不正确"
    return None
