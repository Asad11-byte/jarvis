"""
Supabase client using the service role key (server-side only).
This client bypasses RLS, so all access control happens in our route handlers
(we always scope queries by the authenticated user's id).
"""
from supabase import create_client, Client
from app.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)
