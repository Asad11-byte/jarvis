"""
Encrypt/decrypt OAuth tokens before they touch Supabase.
Never store raw access_token / refresh_token strings in the DB or in logs.
"""
from cryptography.fernet import Fernet
from app.config import settings

_fernet = Fernet(settings.token_encryption_key.encode())


def encrypt_token(raw_value: str) -> str:
    if raw_value is None:
        return None
    return _fernet.encrypt(raw_value.encode()).decode()


def decrypt_token(encrypted_value: str) -> str:
    if encrypted_value is None:
        return None
    return _fernet.decrypt(encrypted_value.encode()).decode()
