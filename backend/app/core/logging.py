import logging

from app.core.secrets_redact import redact_database_url

# Keys whose values are always treated as secret in structured startup logs.
_SENSITIVE_KEY_SUFFIXES = ("_SECRET", "_API_KEY", "_API_SECRET", "_TOKEN", "_PASSWORD")


def _is_sensitive_settings_key(key: str) -> bool:
    if key == "DATABASE_URL":
        return True
    return any(key.endswith(s) for s in _SENSITIVE_KEY_SUFFIXES)


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def safe_settings_log(data: dict) -> dict:
    """Mask secrets and database credentials for safe logging (NFR-S1)."""
    masked: dict = {}
    for k, v in data.items():
        if k == "DATABASE_URL" and v:
            masked[k] = redact_database_url(str(v))
        elif _is_sensitive_settings_key(k) and v:
            masked[k] = "***"
        else:
            masked[k] = v
    return masked
