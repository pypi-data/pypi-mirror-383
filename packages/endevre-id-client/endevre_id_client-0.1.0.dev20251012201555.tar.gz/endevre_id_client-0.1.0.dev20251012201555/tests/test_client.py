from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest

from endevre_id_client import EndevreClient, ExchangeResult
from endevre_id_client.exceptions import TokenError


@dataclass
class FakeResponse:
    payload: Dict[str, Any] | str
    status_code: int = 200
    content_type: str = "application/json"

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            from requests import HTTPError

            raise HTTPError(response=self)

    def json(self) -> Dict[str, Any]:
        if isinstance(self.payload, dict):
            return self.payload
        raise ValueError("Response is not JSON")

    @property
    def headers(self) -> Dict[str, str]:
        return {"Content-Type": self.content_type}

    @property
    def text(self) -> str:
        if isinstance(self.payload, str):
            return self.payload
        return ""


class DummySession:
    def __init__(self, responses: Dict[str, FakeResponse]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, Dict[str, Any]]] = []

    def post(self, url: str, json: Dict[str, Any], timeout: float) -> FakeResponse:
        self.calls.append((url, json))
        try:
            return self._responses[url]
        except KeyError as exc:
            raise AssertionError(f"Unexpected POST to {url}") from exc

    def get(self, url: str, timeout: float) -> FakeResponse:
        try:
            return self._responses[url]
        except KeyError as exc:
            raise AssertionError(f"Unexpected GET to {url}") from exc


def test_get_login_url_places_final_redirect_last() -> None:
    client = EndevreClient("client", "secret")
    url = client.getLoginUrl(
        final_redirect_uri="https://example.com/final",
        redirect_uris=[
            "https://example.com/first",
            "https://example.com/final",
            "https://example.com/second",
        ],
        pairing_id="abc",
    )

    assert "redirectURIs=https%3A%2F%2Fexample.com%2Ffirst%2Chttps%3A%2F%2Fexample.com%2Fsecond%2Chttps%3A%2F%2Fexample.com%2Ffinal" in url
    assert "pairingID=abc" in url


def test_exchange_stores_tokens_and_returns_result() -> None:
    responses = {
        "https://idapi.endevre.com/services/exchange": FakeResponse(
            {
                "token": "token123",
                "refresh": "refresh123",
                "expire": 3600,
                "scopes": ["read", "write"],
            }
        )
    }
    session = DummySession(responses)
    client = EndevreClient("client", "secret", session=session)

    result = client.exchange("code-123")

    assert isinstance(result, ExchangeResult)
    assert result.token == "token123"
    assert result.refresh == "refresh123"
    assert result.scopes == ("read", "write")
    assert session.calls == [
        (
            "https://idapi.endevre.com/services/exchange",
            {
                "clientid": "client",
                "secret": "secret",
                "code": "code-123",
                "jwt": True,
            },
        )
    ]


def test_refresh_token_uses_cached_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "https://idapi.endevre.com/services/exchange": FakeResponse(
            {
                "token": "token123",
                "refresh": "refresh123",
                "expire": 3600,
                "scopes": ["read"],
            }
        ),
        "https://idapi.endevre.com/services/refreshtoken": FakeResponse(
            {
                "token": "token456",
                "refresh": "refresh456",
                "expire": 3600,
            }
        ),
    }
    session = DummySession(responses)
    client = EndevreClient("client", "secret", session=session)
    client.exchange("code-123")

    refreshed = client.refreshToken()

    assert refreshed.token == "token456"
    assert session.calls[-1][1]["refresh"] == "refresh123"


def test_get_user_info_prefers_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    call_args: Dict[str, Any] = {}

    def fake_validate(token: str, **kwargs: Any) -> Dict[str, Any]:
        call_args.update(kwargs)
        return {"user_data": {"firstName": "Ada"}}

    monkeypatch.setattr("endevre_id_client.jwt_utils.validate_jwt", fake_validate)
    monkeypatch.setattr("endevre_id_client.client.validate_jwt", fake_validate)

    responses = {
        "https://idapi.endevre.com/services/exchange": FakeResponse(
            {
                "token": "header.payload.signature",
                "refresh": "refresh123",
                "expire": 3600,
            }
        ),
    }
    session = DummySession(responses)
    client = EndevreClient("client", "secret", session=session)
    client.exchange("code-123")

    user = client.getUserInfo()

    assert user == {"firstName": "Ada"}
    assert call_args["session"] is session


def test_refresh_token_without_cached_value_raises() -> None:
    client = EndevreClient("client", "secret")

    with pytest.raises(TokenError):
        client.refreshToken()
