from datetime import UTC, datetime


def utc_now():
    return datetime.now(UTC)


def utc_now_naive():
    return utc_now().replace(tzinfo=None)


def ensure_utc_naive(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)
