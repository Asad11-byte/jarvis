"""
Centralized app configuration.
All secrets come from environment variables (.env locally, host secrets in prod).
Never hardcode credentials here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_secret_key: str
    frontend_url: str = "http://localhost:5173"

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # Google OAuth scopes requested.
    # gmail.compose intentionally used instead of gmail.modify/gmail.send:
    # it allows creating/editing DRAFTS only, no send capability at the API level.
    google_scopes: list[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/tasks",
    ]

    # Supabase
    supabase_url: str
    supabase_service_role_key: str

    # Token encryption (Fernet key)
    token_encryption_key: str


settings = Settings()
