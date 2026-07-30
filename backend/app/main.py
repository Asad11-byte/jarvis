from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import auth
from app.routers import auth, emails, events, todos, chat

app = FastAPI(title="Jarvis API", version="0.1.0")

# Signs the session cookie that holds our internal user_id.
# This is NOT where Google tokens live -- those are encrypted in Supabase.
app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key, same_site="lax")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,   # required so the session cookie is sent cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(events.router)
app.include_router(todos.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "jarvis-api"}


@app.get("/health")
def health():
    return {"status": "healthy"}

# NOTE: /chat, /emails, /events, /todos routers are added in Phase 2+
# once OAuth + Supabase persistence are verified end-to-end.
