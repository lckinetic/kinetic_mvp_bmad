from __future__ import annotations
from dataclasses import dataclass
import os
from dotenv import load_dotenv


def _bool(v: str | None, default: bool = False) -> bool:
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    mock_mode: bool
    ai_mock_mode: bool
    ai_provider: str
    ai_model: str
    openai_api_key: str
    openai_base_url: str
    ai_timeout_seconds: float

    banxa_api_key: str
    banxa_api_secret: str
    banxa_env: str
    banxa_webhook_secret: str

    log_level: str


def get_settings() -> Settings:
    # Loads backend/.env when you run from backend/
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required (see backend/.env.example).")

    global_mock = _bool(os.getenv("MOCK_MODE"), default=True)
    settings = Settings(
        database_url=database_url,
        mock_mode=global_mock,
        ai_mock_mode=_bool(os.getenv("AI_MOCK_MODE"), default=global_mock),
        ai_provider=os.getenv("AI_PROVIDER", "openai").strip().lower(),
        ai_model=os.getenv("AI_MODEL", "gpt-4o-mini").strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        ai_timeout_seconds=float(os.getenv("AI_TIMEOUT_SECONDS", "20")),

        banxa_api_key=os.getenv("BANXA_API_KEY", ""),
        banxa_api_secret=os.getenv("BANXA_API_SECRET", ""),
        banxa_env=os.getenv("BANXA_ENV", "sandbox"),
        banxa_webhook_secret=os.getenv("BANXA_WEBHOOK_SECRET", ""),

        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    if not settings.ai_mock_mode:
        if settings.ai_provider != "openai":
            raise RuntimeError("When AI is live, AI_PROVIDER must be 'openai'.")
        if not settings.openai_api_key:
            raise RuntimeError("When AI is live, OPENAI_API_KEY is required.")
        if not settings.ai_model:
            raise RuntimeError("When AI is live, AI_MODEL is required.")
    return settings