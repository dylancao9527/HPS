import json
from pathlib import Path
from uuid import uuid4

from flask import current_app

from utils.time_utils import utc_now


def _storage_path():
    configured = current_app.config.get("LOCAL_MOCK_EMAIL_STORE")
    if configured:
        return Path(configured)
    return Path(current_app.root_path) / "runtime" / "mock_emails.json"


def _load_messages(path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_messages(path, messages):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(messages[-100:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def store_email(*, recipient, scene, subject, body, code):
    path = _storage_path()
    messages = _load_messages(path)
    message = {
        "id": str(uuid4()),
        "recipient": recipient,
        "scene": scene,
        "subject": subject,
        "body": body,
        "code": code,
        "created_at": utc_now().isoformat(),
    }
    messages.append(message)
    _save_messages(path, messages)
    return message


def get_latest_email(*, recipient, scene=None):
    path = _storage_path()
    for message in reversed(_load_messages(path)):
        if message.get("recipient") != recipient:
            continue
        if scene and message.get("scene") != scene:
            continue
        return message
    return None
