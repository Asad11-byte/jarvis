# Jarvis — Agentic AI Personal Assistant

Jarvis is a text-based personal assistant that connects to a user's Google
account and autonomously reads mail, drafts replies, and manages a calendar
and to-do list on their behalf — through natural conversation, not forms or
menus. It is built as a **LangGraph ReAct agent**: given a chat message, the
agent reasons about what the user wants, decides which tool(s) it needs,
calls them in whatever order and combination the task requires, observes
the results, and continues until it has a complete answer. No part of the
conversation flow is a hardcoded script — the agent decides its own steps.

> **Hard constraint, by design:** Jarvis can read email and create drafts,
> but it can never send one. This is enforced at two independent layers —
> the OAuth scope granted (`gmail.compose`, which has no send capability at
> the Google API level) and the toolset itself (no "send" tool is ever
> defined, so the agent has no path to reach it even if asked or if a
> prompt-injection attempt tried to talk it into one).

---

## What "agentic" means here

A traditional chatbot maps intents to fixed responses. Jarvis is agentic in
three concrete ways:

1. **Tool use, not scripted flows.** The agent has a toolbox (read email,
   draft email, list/create/update/delete calendar events, list/create/
   update/delete tasks) and an LLM (via Groq) that decides which tools to
   invoke and with what arguments, based on the user's message and the
   results of any tools already called in that turn.
2. **Multi-step reasoning (ReAct loop).** For a request like *"check if
   I'm free Thursday afternoon and if so schedule a call with Sara at 3pm,"*
   the agent has to list events, reason about the result, and only then
   decide to create an event — a sequence it works out for itself, not one
   we coded as an if/else chain.
3. **Grounded, not generative, data.** The system prompt explicitly forbids
   fabricating IDs, dates, email addresses, or event/task details — every
   concrete fact in a response has to come from a real tool call against
   the user's actual Google account.

---

## Architecture

```
┌─────────────┐        ┌──────────────────────────────────────────┐
│   Browser    │        │                 FastAPI                  │
│ (Vite/React) │◄──────►│  Session cookie (signed, httpOnly)        │
└─────────────┘  HTTPS  │                                            │
                         │  /auth/*   — Google OAuth login/callback  │
                         │  /emails   — Gmail read + draft           │
                         │  /events   — Calendar CRUD                │
                         │  /todos    — Tasks CRUD                   │
                         │  /chat     — LangGraph agent               │
                         │                                            │
                         │  ┌──────────────────────────────────┐    │
                         │  │  LangGraph ReAct Agent (Groq LLM) │    │
                         │  │  tools: gmail / calendar / tasks  │    │
                         │  │  built fresh per-request, bound   │    │
                         │  │  to the caller's Google creds     │    │
                         │  └──────────────────────────────────┘    │
                         └──────────────────┬─────────────────────┘
                                             │
                     ┌───────────────────────┼───────────────────────┐
                     ▼                       ▼                       ▼
              ┌─────────────┐        ┌──────────────┐        ┌─────────────┐
              │   Supabase   │        │ Google Gmail  │        │   Google     │
              │  (Postgres)  │        │  Calendar API │        │  Tasks API   │
              │  users,      │        │  (via OAuth   │        │              │
              │  oauth_tokens│        │   credentials)│        │              │
              │  (encrypted),│        └──────────────┘        └─────────────┘
              │  conversations,
              │  messages    │
              └─────────────┘
```

---

## Project structure

```
jarvis-app/
├── backend/                          FastAPI + LangGraph
│   ├── app/
│   │   ├── main.py                   app entrypoint: CORS, session middleware,
│   │   │                             router registration
│   │   ├── config.py                 env-driven settings (pydantic-settings)
│   │   ├── security.py               Fernet encrypt/decrypt for tokens at rest
│   │   ├── database.py               Supabase client (service-role)
│   │   ├── deps.py                   get_authed_user() — resolves session →
│   │   │                             user_id → decrypted, auto-refreshed
│   │   │                             Google credentials, on every request
│   │   ├── models.py                 Pydantic request/response schemas
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py               /auth/login /auth/callback /auth/me /auth/logout
│   │   │   ├── emails.py             GET /emails, GET /emails/{id}, POST /emails/draft
│   │   │   ├── events.py             GET/POST/PATCH/DELETE /events   (Calendar CRUD)
│   │   │   ├── todos.py              GET/POST/PATCH/DELETE /todos    (Tasks CRUD)
│   │   │   └── chat.py               POST /chat — talks to the agent, persists
│   │   │                             conversation history in Supabase
│   │   │
│   │   ├── services/                 thin, agent-agnostic wrappers around the
│   │   │   ├── google_oauth.py       raw Google APIs — used by BOTH the REST
│   │   │   ├── google_clients.py     routers above and the agent's tools, so
│   │   │   ├── gmail_service.py      there is exactly one implementation of
│   │   │   ├── calendar_service.py   each Google operation in the whole app
│   │   │   └── tasks_service.py
│   │   │
│   │   ├── tools/                    LangGraph tool definitions. Each module
│   │   │   ├── gmail_tools.py        exports build_X_tools(service) — a factory
│   │   │   ├── calendar_tools.py     that closes over an already-authenticated
│   │   │   └── task_tools.py         Google API client so the LLM never sees,
│   │   │                             and can never supply, that client itself
│   │   │
│   │   └── agent/
│   │       ├── graph.py              build_agent(credentials) — assembles a
│   │       │                         fresh ReAct agent per request, wired to
│   │       │                         the current user's own Google clients
│   │       └── prompt.py             system prompt: behavior + hard rules
│   │                                 (draft-only, no fabrication, etc.)
│   │
│   ├── supabase_schema.sql           users, oauth_tokens, conversations, messages
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                          Vite + React
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx                    routing + auth guard (Login vs. app shell)
    │   ├── index.css                  design tokens (HUD/assistant aesthetic)
    │   ├── api/
    │   │   └── client.js              axios instance (withCredentials) +
    │   │                              auth/chat/events/todos helper functions
    │   ├── components/
    │   │   ├── Sidebar.jsx            nav + user/logout, hosts the two panels below
    │   │   ├── EventsPanel.jsx        live "upcoming events" list
    │   │   └── TasksPanel.jsx         live task list with toggle-complete/delete
    │   └── pages/
    │       ├── Login.jsx              Google sign-in
    │       ├── Dashboard.jsx          landing page after login
    │       └── Chat.jsx               the conversational interface to Jarvis
    └── .env.example
```

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Agent orchestration | **LangGraph** (`create_react_agent`) | Prebuilt ReAct loop — reasoning, tool-calling, and observation in one graph, without hand-rolling the control flow |
| LLM | **Groq** (`llama-3.3-70b-versatile`) | Fast inference for a responsive chat feel; swappable — see Limitations |
| Backend | **FastAPI** | Async-capable, typed, auto-generated OpenAPI docs at `/docs` |
| Auth | **Google OAuth 2.0** | `gmail.readonly` + `gmail.compose` + `calendar` + `tasks` scopes only — least privilege, and `gmail.compose` structurally cannot send mail |
| Database | **Supabase (Postgres)** | Users, encrypted OAuth tokens, conversation/message history |
| Token storage | **Fernet symmetric encryption** | Access/refresh tokens are ciphertext at rest; only the backend process holds the decryption key |
| Frontend | **Vite + React** | Fast dev loop, no framework lock-in for a small SPA |

---

## Setup

### 1. Google Cloud

1. [Google Cloud Console](https://console.cloud.google.com/) → create/select a project.
2. **APIs & Services → Library** → enable **Gmail API**, **Google Calendar API**, **Tasks API**.
3. **OAuth consent screen** → External → add your email as a test user (keeps the app in "Testing" mode — see Limitations for what this caps).
4. **Credentials → Create Credentials → OAuth client ID** → Web application.
   - Redirect URI: `http://localhost:8000/auth/callback` (add the production URL here too once deployed).
5. Copy the **Client ID** and **Client Secret**.

### 2. Supabase

1. Create a project at [supabase.com](https://supabase.com).
2. Run `backend/supabase_schema.sql` in the SQL editor.
3. Copy the **Project URL** and **service_role key** (Settings → API).

### 3. Groq

1. Create an API key at [console.groq.com](https://console.groq.com).

### 4. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows (Git Bash): source venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env
# fill in: GOOGLE_CLIENT_ID/SECRET, SUPABASE_URL/SERVICE_ROLE_KEY,
#          GROQ_API_KEY, APP_SECRET_KEY, TOKEN_ENCRYPTION_KEY
# generate TOKEN_ENCRYPTION_KEY with:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

uvicorn app.main:app --reload --port 8000
```

### 5. Frontend

```bash
cd frontend
npm install
cp .env.example .env    # VITE_API_URL=http://localhost:8000
npm run dev
```

### 6. Verify end-to-end

1. Open `http://localhost:5173` → **Continue with Google** → grant access → land on `/dashboard`.
2. Check Supabase: a row in `users`, a row in `oauth_tokens` with ciphertext (not readable JWTs) in the token columns.
3. Go to **Chat**, send *"what's on my calendar today?"* — confirms the agent, tool wiring, and live Google data all work together.
4. Ask it to *"draft an email to test@example.com saying hi"* → check Gmail **Drafts** (not Sent) to confirm the constraint holds in practice, not just in theory.

---

## API reference

| Method | Path | Description |
|---|---|---|
| GET | `/auth/login` | Redirect to Google consent screen |
| GET | `/auth/callback` | OAuth callback; sets session cookie |
| GET | `/auth/me` | Current logged-in user |
| POST | `/auth/logout` | Clear session |
| GET | `/emails` | List/summarize recent messages |
| GET | `/emails/{id}` | Full message detail |
| POST | `/emails/draft` | Create a Gmail draft (never sends) |
| GET / POST | `/events` | List / create calendar events |
| PATCH / DELETE | `/events/{id}` | Update / delete a calendar event |
| GET / POST | `/todos` | List / create tasks |
| PATCH / DELETE | `/todos/{id}` | Update / delete a task |
| POST | `/chat` | Send a message to the agent; returns `{conversation_id, response}` |

Full interactive docs at `http://localhost:8000/docs` once the backend is running.

---

## Security design

- **Session cookie, not JWT-in-localStorage.** A signed, httpOnly cookie holds only an internal `user_id`. It is never readable by client-side JS, which rules out XSS-based session theft.
- **Google tokens never reach the browser.** They're encrypted with Fernet and stored server-side in Supabase; decrypted only in-memory, per-request, inside `get_authed_user`.
- **Least-privilege OAuth scopes.** `gmail.compose` rather than `gmail.modify`/`mail.google.com` — draft-only is a scope-level guarantee, not just a prompt instruction.
- **No send-capable tool exists in code.** Even a successful prompt-injection or model hallucination has no reachable send function to call — the capability was never wired in, not merely discouraged.
- **Auto-refresh with re-persistence.** Expired access tokens are refreshed transparently per-request and the new token is re-encrypted and written back to Supabase.

---

## Limitations (current state)

- **Google OAuth "Testing" mode** — capped at 100 test users and requires each tester's email to be added manually in Cloud Console. Moving to production requires Google's app verification process (not yet done).
- **Single LLM provider, no fallback.** If Groq has an outage or rate-limits the app, `/chat` fails outright — there's no fallback provider or retry/backoff logic yet.
- **No streaming responses.** The agent's full reply is generated before anything is sent to the frontend — no token-by-token streaming, so longer multi-tool responses feel slower than they need to.
- **Sidebar doesn't auto-refresh after chat actions.** If you ask the agent to create a task, the Tasks panel won't reflect it until the panel is manually reloaded (page refresh) — there's no shared state or event bus between the chat and sidebar yet.
- **Conversation history has no trimming/summarization.** Every prior message in a conversation is loaded and sent to the LLM on every turn — long conversations will eventually hit context-window and cost limits with no graceful degradation.
- **Tasks are limited to the default list (`@default`).** Multiple Google Task lists aren't supported — everything reads/writes the user's one default list.
- **Update endpoints accept a loosely-typed `dict`.** `PATCH /events/{id}` and `PATCH /todos/{id}` (and the agent's equivalent tools) take a free-form `updates` object rather than a strictly validated schema — fine for now, but it means bad input fails at the Google API layer rather than at our own validation layer.
- **Row Level Security is enabled but unused.** Supabase tables have RLS turned on, but the backend uses the service-role key (which bypasses RLS) for everything — access control is enforced entirely in application code, not at the database layer.
- **No automated tests.** Everything so far has been verified by manual testing against a live Google account — there's no test suite (unit, integration, or agent-behavior eval) yet.
- **No production deployment yet.** Currently local-only (`localhost:8000` / `localhost:5173`); Phase 4 (deployment, prod redirect URI, CORS/session-cookie settings for a real domain) is planned but not done.
- **No observability into agent decisions.** There's no tracing (e.g. LangSmith) showing which tools the agent considered or why — debugging a wrong tool call currently means reading raw responses.

---

## Roadmap / planned improvements

- [ ] **Deploy** (Phase 4) — Dockerize backend, host on Render/Railway/Fly.io, deploy frontend to Vercel, register production OAuth redirect URI.
- [ ] Stream `/chat` responses (Server-Sent Events or WebSocket) for real-time token output.
- [ ] Push sidebar refresh after any chat turn that used a calendar/task tool (shared state via React context, or a lightweight event emitted from `Chat.jsx`).
- [ ] Message history trimming/summarization once a conversation exceeds a token budget.
- [ ] Strict Pydantic schemas for event/task updates instead of free-form `dict`.
- [ ] Move Supabase access to per-user JWTs + real RLS policies, retiring the service-role key from request-time code paths.
- [ ] Add retry/backoff for transient Google API errors (429/5xx) in the service layer.
- [ ] Add an eval/test suite: unit tests for services, integration tests for routers, and behavioral tests for the agent (e.g. "never produces a send action regardless of prompt").
- [ ] Tracing/observability for agent tool-selection (LangSmith or equivalent).
- [ ] Support multiple Google Task lists, not just `@default`.
- [ ] Google app verification to exit OAuth "Testing" mode and remove the 100-user cap.
- [ ] Optional secondary LLM provider as a fallback if Groq is unavailable.

---

## Design decisions worth knowing about

- **Tools are rebuilt per request, not once at startup.** `build_agent(credentials)` constructs fresh Google API clients and binds them into new tool closures on every `/chat` call. This costs a small amount of latency but is what guarantees one user's request can never reach another user's mailbox, calendar, or tasks — there is no shared/global agent object holding anyone's credentials.
- **Service functions are the single source of truth.** `gmail_service.py`, `calendar_service.py`, and `tasks_service.py` are called by both the REST routers *and* the agent's tools — so there is exactly one code path per Google operation, not two implementations that could drift apart.
- **`gmail_service.py` contains no send function, period.** This isn't a disabled/commented-out function — the capability doesn't exist in the codebase at all, which is a stronger guarantee than any runtime check could be.