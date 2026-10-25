import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), encoding="utf-8-sig")


def _default_database_url() -> str:
    """Use a local SQLite database by default so the app runs without external services."""
    db_path = os.path.join(BASE_DIR, "civiccare.db")
    return f"sqlite:///{db_path.replace('\\', '/')}"


def _normalize_database_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return _default_database_url()
    if url.startswith("sqlite:////") and len(url) > 12 and url[11:13].lower() in {"d:", "c:", "e:", "f:", "g:"}:
        return url.replace("sqlite:////", "sqlite:///")
    return url


class Settings:
    DATABASE_URL: str = _normalize_database_url(os.getenv("DATABASE_URL", ""))

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # --- SMS notifications (Twilio) ---
    # Leave these blank to run in "demo mode": SMS messages are printed to the
    # server console/log instead of actually being sent. Fill them in with a
    # real Twilio account to send live SMS to citizens when a complaint is resolved.
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_MB: int = 5

settings = Settings()
