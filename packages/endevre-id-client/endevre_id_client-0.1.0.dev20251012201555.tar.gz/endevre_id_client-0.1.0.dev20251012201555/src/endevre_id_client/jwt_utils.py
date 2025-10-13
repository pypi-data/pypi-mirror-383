from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

import jwt
import requests

from .constants import PUBLIC_KEY_URL
from .exceptions import JWTValidationError, RequestError

_PUBLIC_KEY_CACHE: Dict[str, Any] = {"value": None, "timestamp": 0.0}
_PUBLIC_KEY_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours
_CACHE_LOCK = threading.Lock()


def is_jwt(token: str) -> bool:
    """Return True if the token looks like a JWT."""
    return token.count(".") == 2 and all(part for part in token.split("."))


def decode_jwt(token: str) -> Dict[str, Any]:
    """Decode a JWT without verifying the signature."""
    try:
        return jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
    except jwt.PyJWTError as exc:
        raise JWTValidationError(f"Failed to decode JWT: {exc}") from exc


def fetch_public_key(*, force_refresh: bool = False, timeout: float = 10.0, session: Optional[requests.Session] = None) -> str:
    """Fetch and cache the RSA public key used to sign tokens."""
    with _CACHE_LOCK:
        cached_value = _PUBLIC_KEY_CACHE.get("value")
        cached_age = time.time() - _PUBLIC_KEY_CACHE.get("timestamp", 0.0)
        if not force_refresh and cached_value and cached_age < _PUBLIC_KEY_CACHE_TTL_SECONDS:
            return cached_value

    try:
        if session is not None:
            response = session.get(PUBLIC_KEY_URL, timeout=timeout)
        else:
            response = requests.get(PUBLIC_KEY_URL, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        message = response.text if "response" in locals() else str(exc)
        raise RequestError(f"Failed to fetch public key: {message}", status_code=getattr(response, "status_code", None)) from exc
    except requests.RequestException as exc:
        raise RequestError(f"Failed to fetch public key: {exc}") from exc

    public_key = response.text.strip()

    with _CACHE_LOCK:
        _PUBLIC_KEY_CACHE["value"] = public_key
        _PUBLIC_KEY_CACHE["timestamp"] = time.time()

    return public_key


def validate_jwt(token: str, *, public_key: Optional[str] = None, session: Optional[requests.Session] = None, force_refresh_key: bool = False, timeout: float = 10.0) -> Dict[str, Any]:
    """Validate a JWT and return its payload.

    Raises :class:`JWTValidationError` if validation fails.
    """
    if not is_jwt(token):
        raise JWTValidationError("Token is not a JWT")

    key = public_key
    last_error: Optional[Exception] = None

    for attempt, refresh in enumerate((False, force_refresh_key), start=1):
        if key is None or refresh:
            try:
                key = fetch_public_key(force_refresh=refresh, timeout=timeout, session=session)
            except RequestError as exc:
                last_error = exc
                continue

        try:
            return jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise JWTValidationError("JWT token has expired") from exc
        except jwt.PyJWTError as exc:
            last_error = exc
            # On first failure retry with refreshed key if allowed
            continue

    if last_error is not None:
        raise JWTValidationError(f"JWT validation failed: {last_error}") from last_error
    raise JWTValidationError("JWT validation failed")


def get_user_data_from_jwt(token: str) -> Dict[str, Any]:
    payload = decode_jwt(token)
    user_data = payload.get("user_data")
    if isinstance(user_data, dict):
        return user_data
    return payload
