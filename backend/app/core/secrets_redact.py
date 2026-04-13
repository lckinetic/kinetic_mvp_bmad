from __future__ import annotations

from urllib.parse import urlparse, urlunparse

from app.core.config import Settings


def redact_database_url(url: str) -> str:
    """Return a copy of *url* with credentials masked (user password in netloc)."""
    if not url or not isinstance(url, str):
        return url
    try:
        parsed = urlparse(url)
        if not parsed.password:
            return url
        host = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        user = parsed.username or ""
        auth = f"{user}:***" if user else "***"
        new_netloc = f"{auth}@{host}{port}"
        return urlunparse(parsed._replace(netloc=new_netloc))
    except Exception:
        return "<redacted DATABASE_URL>"


def _secret_substrings(settings: Settings) -> list[str]:
    """Non-empty secret material that must not appear in logs or client-visible errors."""
    out: list[str] = []
    for s in (
        settings.banxa_api_key,
        settings.banxa_api_secret,
        settings.banxa_webhook_secret,
    ):
        if s and len(s.strip()) > 0:
            out.append(s)
    try:
        parsed = urlparse(settings.database_url)
        if parsed.password:
            out.append(parsed.password)
    except Exception:
        pass
    # Longest first so nested/overlapping replacements stay stable
    return sorted(set(out), key=len, reverse=True)


def redact_secrets_in_text(text: str, settings: Settings) -> str:
    """Replace known configured secrets if they appear inside *text* (e.g. exception messages)."""
    if not text:
        return text
    redacted = text
    for secret in _secret_substrings(settings):
        if secret in redacted:
            redacted = redacted.replace(secret, "***")
    return redacted
