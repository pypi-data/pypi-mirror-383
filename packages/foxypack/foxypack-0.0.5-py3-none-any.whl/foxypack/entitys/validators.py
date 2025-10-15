import base64
import re
from enum import Enum
from urllib.parse import urlparse

from .exceptions import (
    ProxyValidationError,
    InstagramValidationError,
    TelegramValidationError,
)
from .serializer import EnumSerializer


def validate_count(value: int | float, source: str):
    if value < 0:
        raise ValueError(f"New value for '{source}' is lesser then 0")


def validate_proxy(proxy: str) -> None:
    parsed = urlparse(proxy)

    if parsed.scheme not in ("http", "socks4", "socks5"):
        raise ProxyValidationError(f"Unsupported proxy scheme: '{parsed.scheme}'")

    if not parsed.hostname:
        raise ProxyValidationError("Proxy host is missing")

    if not parsed.port:
        raise ProxyValidationError("Proxy port is missing or invalid")

    if not (0 < parsed.port < 65536):
        raise ProxyValidationError(f"Proxy port out of range: {parsed.port}")

    if not re.match(r"^([a-zA-Z0-9.\-_]+|\[[0-9a-fA-F:]+\])$", parsed.hostname):
        raise ProxyValidationError(f"Invalid hostname: {parsed.hostname}")

    if parsed.username and ":" in parsed.username:
        raise ProxyValidationError("Username must not contain ':'")

    if parsed.password and "@" in parsed.password:
        raise ProxyValidationError("Password must not contain '@'")


def validate_instagram_session_id(session_id: str) -> None:
    if not isinstance(session_id, str) or not session_id:
        raise InstagramValidationError("SessionID must be a non-empty string")
    if not re.fullmatch(r"[0-9a-zA-Z%]+", session_id):
        raise InstagramValidationError("Invalid Instagram SessionID format")


def validate_instagram_csrf(csrf_token: str) -> None:
    if not isinstance(csrf_token, str) or not csrf_token:
        raise InstagramValidationError("CSRF token must be a non-empty string")
    if not re.fullmatch(r"[0-9a-zA-Z]{8,}", csrf_token):
        raise InstagramValidationError("Invalid Instagram CSRF token format")


def validate_telegram_api_id(api_id: str | int) -> None:
    try:
        api_id = int(api_id)
    except (ValueError, TypeError):
        raise TelegramValidationError("Telegram api_id must be an integer")

    if not (10000 <= api_id <= 999999999):
        raise TelegramValidationError(
            "Telegram api_id must be in the valid range (10000–9999999)"
        )


def validate_telegram_api_hash(api_hash: str) -> None:
    if not isinstance(api_hash, str):
        raise TelegramValidationError("Telegram api_hash must be a string")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", api_hash):
        raise TelegramValidationError(
            "Telegram api_hash must be a 32-character hex string"
        )


def validate_telegram_session_token(token: str) -> None:
    if not isinstance(token, str) or not token.strip():
        raise TelegramValidationError(
            "Telegram session token must be a non-empty string"
        )

    try:
        base64.urlsafe_b64decode(token + "==")
    except Exception:
        raise TelegramValidationError("Invalid Telegram session token format")


def resolve_enum(enum_str: str) -> Enum:
    return EnumSerializer.resolve_enum(enum_str)
