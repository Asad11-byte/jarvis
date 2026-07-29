"""
Wraps google-auth-oauthlib to:
  1. build the consent-screen URL
  2. exchange the returned ?code= for tokens
  3. fetch basic profile info (id, email, name, picture)
  4. refresh an expired access token

Nothing in this file ever imports or calls a Gmail "send" endpoint on purpose --
the send capability is excluded at the scope level (see config.py: gmail.compose).
"""
from datetime import datetime, timezone

import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest

from app.config import settings

USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"


def _client_config() -> dict:
    return {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }


def build_authorization_url(state: str) -> str:
    flow = Flow.from_client_config(
        _client_config(),
        scopes=settings.google_scopes,
        state=state,
    )
    flow.redirect_uri = settings.google_redirect_uri

    auth_url, _ = flow.authorization_url(
        access_type="offline",     # required to get a refresh_token
        prompt="consent",          # forces refresh_token on every login, not just the first
        include_granted_scopes="true",
    )
    return auth_url


def exchange_code_for_tokens(code: str, state: str) -> Credentials:
    flow = Flow.from_client_config(
        _client_config(),
        scopes=settings.google_scopes,
        state=state,
    )
    flow.redirect_uri = settings.google_redirect_uri
    flow.fetch_token(code=code)
    return flow.credentials


def fetch_userinfo(credentials: Credentials) -> dict:
    resp = requests.get(
        USERINFO_ENDPOINT,
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()  # {sub, email, name, picture, ...}


def credentials_from_stored(
    access_token: str,
    refresh_token: str | None,
    scopes: list[str],
) -> Credentials:
    return Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=scopes,
    )


def refresh_if_needed(credentials: Credentials) -> Credentials:
    """Refreshes in place if expired/near-expired. Caller persists the new token."""
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())
    return credentials


def credentials_expiry_utc(credentials: Credentials) -> datetime:
    if credentials.expiry is None:
        return datetime.now(timezone.utc)
    # google-auth stores naive UTC datetimes
    return credentials.expiry.replace(tzinfo=timezone.utc)
