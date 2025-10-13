# Endevre ID Python Client

A Python helper library for interacting with Endevre ID authentication services. It mirrors the core workflows of the browser client with a server-friendly API.

## Features

- Build secure login URLs for Endevre ID SSO flows.
- Exchange authorization codes for tokens (optionally requesting JWTs).
- Refresh access tokens using stored refresh tokens.
- Retrieve user information from tokens or the Endevre ID API.
- Optional JWT validation backed by the public signing key.

## Installation

```bash
pip install endevre-id-client
```

## Quick start

```python
from endevre_id_client import EndevreClient

client = EndevreClient(
    client_id="<your client id>",
    client_secret="<your client secret>",
)

login_url = client.getLoginUrl(
    final_redirect_uri="https://app.example.com/auth/callback",
    redirect_uris=["https://app.example.com/start"],
)

# After your user completes the flow and you receive the `code`
exchange_result = client.exchange(code)
user_info = client.getUserInfo(exchange_result.token)
refreshed = client.refreshToken(exchange_result.refresh)
```

## Publishing

Automated publishing mirrors the JavaScript package strategy:

- Pushes to `main` publish the version defined in `pyproject.toml` as the stable release.
- Pushes to `beta` publish a time-stamped beta pre-release (e.g. `0.1.0b20241006123000+gabc1234`).
- Pushes to `dev` publish a time-stamped development build (e.g. `0.1.0.dev20241006123000+gabc1234`).
- Pushes to `justin*` / `ray*` branches run tests only (no publish).

All workflows live under `.github/workflows/python-ci-cd.yml` and rely on the `PYPI_API_TOKEN` secret (or PyPI Trusted Publisher configuration) for auth.

## Development

Install dev dependencies:

```bash
pip install -e .[dev]
```

Run the test suite:

```bash
pytest
```
