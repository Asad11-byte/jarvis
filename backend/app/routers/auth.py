"""
Google OAuth login/callback + session endpoints.

Flow:
  GET  /auth/login     -> redirect browser to Google consent screen
  GET  /auth/callback  -> Google redirects here with ?code=&state=
                           we exchange the code, upsert the user + encrypted
                           tokens in Supabase, set a session cookie, then
                           redirect back to the frontend.
  GET  /auth/me        -> return the logged-in user (reads session cookie)
  POST /auth/logout    -> clear session cookie
"""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from app.config import settings
from app.database import supabase
from app.security import encrypt_token
from app.services import google_oauth

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_COOKIE = "oauth_state"
SESSION_COOKIE = "jarvis_session"  # holds our internal user_id, signed by SessionMiddleware


@router.get("/login")
def login():
    state = secrets.token_urlsafe(24)
    auth_url = google_oauth.build_authorization_url(state=state)

    response = RedirectResponse(auth_url)
    # short-lived cookie just to validate state on callback (CSRF protection)
    response.set_cookie(
        STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        secure=settings.app_env != "development",
        samesite="lax",
    )
    return response


@router.get("/callback")
def callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    expected_state = request.cookies.get(STATE_COOKIE)
    if not code or not state or not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state or missing code")

    credentials = google_oauth.exchange_code_for_tokens(code=code, state=state)
    profile = google_oauth.fetch_userinfo(credentials)

    google_sub = profile["sub"]
    email = profile.get("email")
    full_name = profile.get("name")
    avatar_url = profile.get("picture")

    # Upsert user
    existing = supabase.table("users").select("id").eq("google_sub", google_sub).execute()
    if existing.data:
        user_id = existing.data[0]["id"]
        supabase.table("users").update({
            "email": email,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", user_id).execute()
    else:
        inserted = supabase.table("users").insert({
            "google_sub": google_sub,
            "email": email,
            "full_name": full_name,
            "avatar_url": avatar_url,
        }).execute()
        user_id = inserted.data[0]["id"]

    # Store encrypted tokens.
    # Google only returns refresh_token on first consent (or when prompt=consent forces it,
    # which we always pass) -- if it's missing, keep whatever we already have stored.
    expiry = google_oauth.credentials_expiry_utc(credentials)
    token_row = {
        "user_id": user_id,
        "access_token_enc": encrypt_token(credentials.token),
        "scopes": " ".join(credentials.scopes or settings.google_scopes),
        "expiry": expiry.isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if credentials.refresh_token:
        token_row["refresh_token_enc"] = encrypt_token(credentials.refresh_token)

    supabase.table("oauth_tokens").upsert(token_row, on_conflict="user_id").execute()

    # Establish app session (signed cookie, not the raw Google token)
    request.session["user_id"] = user_id

    response = RedirectResponse(f"{settings.frontend_url}/dashboard")
    response.delete_cookie(STATE_COOKIE)
    return response


@router.get("/me")
def me(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = supabase.table("users").select("id,email,full_name,avatar_url").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User not found")
    return result.data[0]


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}
