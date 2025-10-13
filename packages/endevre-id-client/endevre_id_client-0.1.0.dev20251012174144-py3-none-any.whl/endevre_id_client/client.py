from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Sequence
from urllib.parse import urlencode

import requests

from .constants import EXCHANGE_URL, REFRESH_URL, USERINFO_URL, SSO_LOGIN_BASE
from .exceptions import ConfigurationError, JWTValidationError, RequestError, TokenError
from .jwt_utils import is_jwt, validate_jwt

LOGGER = logging.getLogger(__name__)


def _normalize_scopes(value: Any) -> Optional[tuple[str, ...]]:
    if value is None:
        return None
    if isinstance(value, str):
        parts = [segment.strip() for segment in value.split() if segment.strip()]
        return tuple(parts) if parts else None
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        parts = [str(segment).strip() for segment in value if str(segment).strip()]
        return tuple(parts) if parts else None
    return (str(value).strip(),) if str(value).strip() else None


@dataclass(frozen=True, slots=True)
class ExchangeResult:
    token: str
    refresh: str
    expire: int
    scopes: Optional[tuple[str, ...]] = None
    raw: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ExchangeResult":
        try:
            token = str(payload["token"])
            refresh = str(payload["refresh"])
            expire = int(payload["expire"])
        except KeyError as exc:
            raise RequestError(f"Missing expected field in exchange response: {exc}") from exc
        scopes = _normalize_scopes(payload.get("scopes"))
        return cls(token=token, refresh=refresh, expire=expire, scopes=scopes, raw=dict(payload))

    def as_dict(self) -> Dict[str, Any]:
        data = dict(self.raw)
        data.setdefault("token", self.token)
        data.setdefault("refresh", self.refresh)
        data.setdefault("expire", self.expire)
        if self.scopes is not None:
            data.setdefault("scopes", list(self.scopes))
        return data


@dataclass(frozen=True, slots=True)
class RefreshResult:
    token: str
    refresh: str
    expire: int
    raw: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RefreshResult":
        try:
            token = str(payload["token"])
            refresh = str(payload["refresh"])
            expire = int(payload["expire"])
        except KeyError as exc:
            raise RequestError(f"Missing expected field in refresh response: {exc}") from exc
        return cls(token=token, refresh=refresh, expire=expire, raw=dict(payload))

    def as_dict(self) -> Dict[str, Any]:
        data = dict(self.raw)
        data.setdefault("token", self.token)
        data.setdefault("refresh", self.refresh)
        data.setdefault("expire", self.expire)
        return data


class EndevreClient:
    """Python client for Endevre ID authentication APIs."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        session: Optional[requests.Session] = None,
        default_timeout: float = 10.0,
    ) -> None:
        if not client_id or not client_secret:
            raise ConfigurationError("client_id and client_secret are required")
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = session or requests.Session()
        self._default_timeout = default_timeout
        self._latest_exchange: Optional[ExchangeResult] = None

    # Aliases for TypeScript-style naming
    def get_login_url(
        self,
        *,
        final_redirect_uri: str,
        redirect_uris: Iterable[str],
        pairing_id: Optional[str] = None,
        **extra_params: Any,
    ) -> str:
        final_uri = str(final_redirect_uri).strip()
        if not final_uri:
            raise ConfigurationError("final_redirect_uri is required")

        redirect_list = [str(uri).strip() for uri in redirect_uris if str(uri).strip()]
        redirect_list = [uri for uri in redirect_list if uri != final_uri]
        redirect_list.append(final_uri)

        params: Dict[str, Any] = {
            "clientID": self._client_id,
            "redirectURIs": ",".join(redirect_list),
        }
        if pairing_id is not None:
            params["pairingID"] = pairing_id

        for key, value in extra_params.items():
            if value is None:
                continue
            params[key] = value

        return f"{SSO_LOGIN_BASE}?{urlencode(params)}"

    # CamelCase alias for JS parity
    getLoginUrl = get_login_url  # type: ignore[assignment]

    def exchange(self, code: str, *, use_jwt: bool = True, timeout: Optional[float] = None) -> ExchangeResult:
        payload = {
            "clientid": self._client_id,
            "secret": self._client_secret,
            "code": code,
            "jwt": use_jwt,
        }
        data = self._post(EXCHANGE_URL, payload, timeout=timeout)
        result = ExchangeResult.from_dict(data)
        self._latest_exchange = result
        return result

    def refresh_token(self, refresh: Optional[str] = None, *, use_jwt: bool = True, timeout: Optional[float] = None) -> RefreshResult:
        refresh_token_value = refresh or (self._latest_exchange.refresh if self._latest_exchange else None)
        if not refresh_token_value:
            raise TokenError("No refresh token available; call exchange() with a valid code first")

        payload = {
            "clientid": self._client_id,
            "secret": self._client_secret,
            "refresh": refresh_token_value,
            "jwt": use_jwt,
        }
        data = self._post(REFRESH_URL, payload, timeout=timeout)
        result = RefreshResult.from_dict(data)
        if self._latest_exchange is not None:
            self._latest_exchange = ExchangeResult(
                token=result.token,
                refresh=result.refresh,
                expire=result.expire,
                scopes=self._latest_exchange.scopes,
                raw={**self._latest_exchange.raw, **result.raw},
            )
        else:
            self._latest_exchange = ExchangeResult(
                token=result.token,
                refresh=result.refresh,
                expire=result.expire,
                scopes=None,
                raw=result.raw,
            )
        return result

    def get_user_info(
        self,
        token: Optional[str] = None,
        *,
        validate_jwt_signature: bool = True,
        force_refresh_key: bool = False,
        timeout: Optional[float] = None,
    ) -> Mapping[str, Any]:
        token_value = token or (self._latest_exchange.token if self._latest_exchange else None)
        if not token_value:
            raise TokenError("No token available; pass a token or call exchange() first")

        if validate_jwt_signature and is_jwt(token_value):
            try:
                payload = validate_jwt(
                    token_value,
                    session=self._session,
                    force_refresh_key=force_refresh_key,
                    timeout=timeout or self._default_timeout,
                )
                return payload.get("user_data", payload)
            except JWTValidationError as exc:
                LOGGER.warning("JWT validation failed, falling back to userinfo endpoint: %s", exc)

        payload = {"clientid": self._client_id, "token": token_value}
        data = self._post(USERINFO_URL, payload, timeout=timeout)
        return data

    def _post(self, url: str, payload: MutableMapping[str, Any], *, timeout: Optional[float]) -> Dict[str, Any]:
        try:
            response = self._session.post(url, json=payload, timeout=timeout or self._default_timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            message = _extract_error_message(response)
            raise RequestError(message, status_code=response.status_code, response=_safe_json(response)) from exc
        except requests.RequestException as exc:
            raise RequestError(f"HTTP request failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise RequestError("Expected JSON response but received invalid JSON") from exc


    # Aliases for API parity
    refreshToken = refresh_token  # type: ignore[assignment]
    getUserInfo = get_user_info  # type: ignore[assignment]


def _extract_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
        for key in ("message", "error", "detail", "error_message"):
            if key in payload:
                return str(payload[key])
        return str(payload)
    except ValueError:
        text = response.text.strip()
        return text or f"HTTP {response.status_code}"


def _safe_json(response: requests.Response) -> Optional[Mapping[str, Any]]:
    try:
        data = response.json()
        if isinstance(data, Mapping):
            return data
    except ValueError:
        return None
    return None


def create_client(client_id: str, client_secret: str, **kwargs: Any) -> EndevreClient:
    return EndevreClient(client_id, client_secret, **kwargs)
