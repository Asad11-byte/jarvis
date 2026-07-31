from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
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

# Prefixed with /api so backend routes can never collide with frontend
# routes on the same domain in the monorepo deployment (e.g. the frontend
# has a page at /chat, and the backend has an endpoint at /chat -- the
# prefix is what keeps those distinct once both are served from one origin).
app.include_router(auth.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(todos.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api")
def root():
    return {"status": "ok", "service": "jarvis-api"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}