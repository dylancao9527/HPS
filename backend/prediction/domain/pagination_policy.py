DEFAULT_PAGE = 1
DEFAULT_HISTORY_PAGE_SIZE = 10
DEFAULT_GOVERNANCE_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def normalize_page(page, *, default=DEFAULT_PAGE):
    try:
        value = int(page)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def normalize_per_page(per_page, *, default, maximum=MAX_PAGE_SIZE):
    try:
        value = int(per_page)
    except (TypeError, ValueError):
        return default
    if value <= 0:
        return default
    return min(value, maximum)
