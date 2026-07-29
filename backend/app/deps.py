"""
Shared FastAPI dependency used by every data route (/emails, /events, /todos, /chat later).

Responsibilities:
  1. Read user_id from the session cookie (401 if not logged in)
  2. Load the user's encrypted tokens from Supabase
  3. Decrypt + build google.oauth2.credentials.Credentials
  4. Refresh if expired, and persist the new access token back to Supabase
     (refresh_token stays the same unless Google issues a new one)
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Request, HTTPException
from google.oauth2.credentials import Credentials

from app.database import supabase
from app.security import encrypt_token, decrypt_token
from app.services import google_oauth


@dataclass
class AuthedUser:
    user_id: str
    credentials: Credentials


def get_current_user_id(request: Request) -> str:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


def get_authed_user(request: Request) -> AuthedUser:
    user_id = get_current_user_id(request)

    result = supabase.table("oauth_tokens").select("*").eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="No Google account linked. Please log in again.")

    row = result.data[0]
    access_token = decrypt_token(row["access_token_enc"])
    refresh_token = decrypt_token(row["refresh_token_enc"]) if row.get("refresh_token_enc") else None
    scopes = row["scopes"].split(" ")

    credentials = google_oauth.credentials_from_stored(
        access_token=access_token,
        refresh_token=refresh_token,
        scopes=scopes,
    )
    # Force expiry so google-auth knows whether a refresh is needed
    credentials.expiry = datetime.fromisoformat(row["expiry"]).replace(tzinfo=None)

    was_expired = not credentials.valid
    credentials = google_oauth.refresh_if_needed(credentials)

    if was_expired:
        # persist the newly refreshed access token (+ new expiry) back to Supabase
        supabase.table("oauth_tokens").update({
            "access_token_enc": encrypt_token(credentials.token),
            "expiry": google_oauth.credentials_expiry_utc(credentials).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("user_id", user_id).execute()

    return AuthedUser(user_id=user_id, credentials=credentials)