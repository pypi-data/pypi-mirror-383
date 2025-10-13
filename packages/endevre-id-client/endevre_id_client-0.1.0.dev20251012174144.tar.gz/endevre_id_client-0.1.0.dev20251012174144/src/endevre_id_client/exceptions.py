from __future__ import annotations

from typing import Any, Mapping, Optional


class EndevreAuthError(Exception):
    """Base exception for the Endevre ID Python client."""


class ConfigurationError(EndevreAuthError):
    """Raised when required configuration values are missing or invalid."""


class RequestError(EndevreAuthError):
    """Raised when an HTTP request returns an error response."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, response: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TokenError(EndevreAuthError):
    """Raised when token operations fail or inputs are missing."""


class JWTValidationError(EndevreAuthError):
    """Raised when JWT validation fails."""
