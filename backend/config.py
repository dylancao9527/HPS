import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is required. Configure the MySQL connection in backend/.env."
        )
    return value


class Config:
    SQLALCHEMY_DATABASE_URI = _required_env("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "local-dev-secret-key-change-me-at-least-32-bytes",
    )
    JWT_EXPIRATION_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123456")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@hypertension.local")
    INIT_ADMIN_ON_STARTUP = os.getenv("INIT_ADMIN_ON_STARTUP", "1") == "1"

    EXPORT_RECENT_BP_COUNT = int(os.getenv("EXPORT_RECENT_BP_COUNT", "5"))

    ENABLE_LOCAL_MOCK_EMAIL_SERVICE = (
        os.getenv("ENABLE_LOCAL_MOCK_EMAIL_SERVICE", "1") == "1"
    )
    LOCAL_MOCK_EMAIL_STORE = os.getenv(
        "LOCAL_MOCK_EMAIL_STORE",
        str(BASE_DIR / "runtime" / "mock_emails.json"),
    )

    PROPHET_MAX_TRAIN_DAYS = int(os.getenv("PROPHET_MAX_TRAIN_DAYS", "90"))
    PROPHET_RETRAIN_AFTER_DAYS = int(
        os.getenv("PROPHET_RETRAIN_AFTER_DAYS", "3")
    )
    PROPHET_CACHE_VERSION = os.getenv("PROPHET_CACHE_VERSION", "1")
    PROPHET_MODEL_STORAGE_ROOT = os.getenv(
        "PROPHET_MODEL_STORAGE_ROOT",
        str(BASE_DIR / "runtime" / "prophet_models"),
    )
    PROPHET_MEMORY_CACHE_TTL_SECONDS = int(
        os.getenv("PROPHET_MEMORY_CACHE_TTL_SECONDS", "900")
    )
    PROPHET_MAX_INACTIVE_METADATA_PER_SLOT = int(
        os.getenv("PROPHET_MAX_INACTIVE_METADATA_PER_SLOT", "1")
    )
    PROPHET_CLEANUP_ENABLED = os.getenv("PROPHET_CLEANUP_ENABLED", "1") == "1"
    PROPHET_CLEANUP_MAX_INACTIVE_AGE_HOURS = int(
        os.getenv("PROPHET_CLEANUP_MAX_INACTIVE_AGE_HOURS", "24")
    )
