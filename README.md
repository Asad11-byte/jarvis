# Jarvis — Phase 1: Google OAuth

Text-based personal assistant. This phase wires up **login only**:
Google OAuth → session cookie → user + encrypted tokens stored in Supabase.
Chat, mailbox, calendar, and tasks endpoints come in the next phase.

## Project structure

```
jarvis-app/
├── backend/                 FastAPI
│   ├── app/
│   │   ├── main.py          app entrypoint, CORS + session middleware
│   │   ├── config.py        env-driven settings (pydantic-settings)
│   │   ├── security.py      Fernet encrypt/decrypt for tokens at rest
│   │   ├── database.py      Supabase client
│   │   ├── models.py        Pydantic schemas
│   │   ├── routers/
│   │   │   └── auth.py      /auth/login /auth/callback /auth/me /auth/logout
│   │   └── services/
│   │       └── google_oauth.py   auth URL, code exchange, refresh
│   ├── supabase_schema.sql  run this in Supabase SQL editor first
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 Vite + React
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx           route guard: Login vs Dashboard
    │   ├── api/client.js     axios instance (withCredentials) + auth helpers
    │   └── pages/
    │       ├── Login.jsx
    │       └── Dashboard.jsx
    └── .env.example
```

## 1. Google Cloud setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create/select a project.
2. **APIs & Services → Library** → enable: **Gmail API**, **Google Calendar API**, **Tasks API**.
3. **APIs & Services → OAuth consent screen** → External → add your email as a test user (keeps you in "Testing" mode, no Google verification needed for a demo).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID** → type **Web application**.
   - Authorized redirect URI (local): `http://localhost:8000/auth/callback`
   - You'll add the deployed URL here too once hosted.
5. Copy the **Client ID** and **Client Secret**.

## 2. Supabase setup

1. Create a project at [supabase.com](https://supabase.com).
2. Open the **SQL editor** and run `backend/supabase_schema.sql`.
3. Copy your **Project URL** and **service_role key** (Settings → API).

## 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# fill in .env:
#   GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET  (step 1)
#   SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY (step 2)
#   APP_SECRET_KEY   -> any long random string
#   TOKEN_ENCRYPTION_KEY -> generate with:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`.

## 4. Frontend

```bash
cd frontend
npm install
cp .env.example .env    # VITE_API_URL=http://localhost:8000
npm run dev
```

Frontend runs at `http://localhost:5173`.

## 5. Test the flow

1. Open `http://localhost:5173`.
2. Click **Continue with Google** → consent screen → grant access.
3. You land on `/dashboard` with your name/email — confirms the session cookie
   and the encrypted-token round trip through Supabase both worked.
4. Check the Supabase table editor: a row in `users` and a row in `oauth_tokens`
   (the token columns should be unreadable ciphertext, not plaintext JWTs).

## Notes on the design choices

- **Session cookie vs JWT-in-localStorage**: we use a signed, httpOnly session
  cookie (`SessionMiddleware`) holding only our internal `user_id`. The actual
  Google access/refresh tokens never reach the browser — they stay encrypted
  in Supabase and are used server-side only.
- **`gmail.compose` scope**: deliberately used instead of `gmail.modify` or
  full `mail.google.com`. It grants draft creation/editing but has no send
  capability at the API level — the "never send" constraint is enforced by
  the OAuth scope itself, not just app logic.
- **`access_type=offline` + `prompt=consent`**: guarantees a `refresh_token`
  comes back on every login so long-lived access works without re-consent.

## Next phase

- `POST /chat` (LangGraph agent)
- `GET /emails`, mailbox read/draft tools
- `GET/POST/PATCH/DELETE /events` (Calendar CRUD)
- `GET/POST/PATCH/DELETE /todos` (Tasks CRUD)
- Deployment (Render/Railway/Fly.io) + production redirect URI
