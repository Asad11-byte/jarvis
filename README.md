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

**Live:** deployed as a single Vercel project (frontend + backend, one
domain). See [Deployment](#deployment) for the exact setup.

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
                         │  /api/auth/*   — Google OAuth login/callback │
                         │  /api/emails   — Gmail read + draft          │
                         │  /api/events   — Calendar CRUD                │
                         │  /api/todos    — Tasks CRUD                   │
                         │  /api/chat     — LangGraph agent               │
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

All backend routes live under an **`/api` prefix** (`/api/auth/login`,
`/api/chat`, etc.) so they can never collide with frontend routes of the
same name on the same domain — notably, the frontend has its own `/chat`
page, distinct from the backend's `/api/chat` endpoint.

---

## Project structure

```
jarvis-app/
├── api/
│   └── index.py                      Vercel entrypoint (repo root, NOT inside
│                                      backend/) — imports the real FastAPI app
│                                      from backend/app/main.py; backend/ is
│                                      bundled alongside it via vercel.json's
│                                      `includeFiles: "backend/**"`
├── requirements.txt                  root-level delegate: `-r backend/requirements.txt`
│                                      (Vercel's Python builder looks for
│                                      requirements.txt near the entrypoint,
│                                      which is now at the repo root)
├── .python-version                   pins Python 3.14 for the Vercel build
├── vercel.json                       single-project monorepo config: builds
│                                      the frontend, wires api/index.py as a
│                                      function, rewrites /api/* to it and
│                                      everything else to the SPA
│
├── backend/                          FastAPI + LangGraph
│   ├── app/
│   │   ├── main.py                   app entrypoint: CORS, session middleware,
│   │   │                             router registration (all under /api)
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
│   │   │                             and can never supply, that client itself.
│   │   │                             Every tool returns json.dumps(...) — some
│   │   │                             LLM providers reject empty-list tool
│   │   │                             content, so results are always JSON strings.
│   │   │
│   │   └── agent/
│   │       ├── graph.py              build_agent(credentials) — assembles a
│   │       │                         fresh ReAct agent per request, wired to
│   │       │                         the current user's own Google clients
│   │       └── prompt.py             system prompt: behavior + hard rules
│   │                                 (draft-only, no fabrication, etc.)
│   │
│   ├── supabase_schema.sql           users, oauth_tokens, conversations, messages
│   ├── requirements.txt              actual pinned dependency list
│   └── .env.example
│
└── frontend/                          Vite + React
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx                    routing + auth guard + mobile sidebar state
    │   ├── index.css                  design tokens + responsive drawer CSS
    │   ├── api/
    │   │   └── client.js              axios instance (withCredentials, baseURL
    │   │                              includes /api) + auth/chat/events/todos
    │   │                              helper functions
    │   ├── components/
    │   │   ├── Sidebar.jsx            nav + user/logout + panels; becomes a
    │   │   │                         slide-in drawer with a backdrop on mobile
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
| Hosting | **Vercel** (single project) | One domain serves both the static frontend build and the Python serverless function, via `vercel.json`'s `functions` + `rewrites` |

---

## Design system / color palette

The frontend uses a dark, HUD-inspired aesthetic (fitting for an assistant
named Jarvis) defined entirely as CSS custom properties in
`frontend/src/index.css`, so every component pulls from the same tokens
rather than hardcoding colors.

| Token | Value | Used for |
|---|---|---|
| `--bg` | `#0a0e14` | Page background (near-black navy) |
| `--surface` | `#10161f` | Sidebar, cards, panel backgrounds |
| `--surface-raised` | `#161e2a` | Nested elements on top of a surface (list items, chat bubbles, inputs) |
| `--border` | `rgba(255, 255, 255, 0.08)` | All hairline borders/dividers |
| `--text` | `#e7edf5` | Primary text |
| `--text-muted` | `#7a8699` | Secondary text, placeholders, timestamps |
| `--accent` | `#49e0d1` | Brand accent ("arc-reactor" cyan) — buttons, active nav state, status indicators |
| `--accent-dim` | `rgba(73, 224, 209, 0.15)` | Accent-tinted backgrounds (active nav link, user chat bubble) |
| `--danger` | `#ff6b6b` | Errors, destructive actions |

**Typography:**

| Token | Font | Used for |
|---|---|---|
| `--font-display` | Space Grotesk (700) | Headings, brand wordmark |
| `--font-body` | Inter | Body text, UI copy |
| `--font-mono` | JetBrains Mono | Status readouts, timestamps, eyebrow labels — reinforces the HUD feel |

All three are loaded from Google Fonts in `index.css`. Because colors and
fonts are tokens, not one-off values, retheming the whole app means editing
the `:root` block in one file rather than hunting through every component.

**Responsive behavior:** the sidebar is a fixed 280px column on desktop.
Below a `768px` viewport width, it becomes a slide-in drawer (off-canvas by
default, triggered by a hamburger button in a mobile top bar, with a
dark backdrop that closes it on tap) — defined via media queries in
`index.css` alongside the color tokens, since inline component styles
can't respond to viewport size on their own.

---

## Setup

### 1. Google Cloud

1. [Google Cloud Console](https://console.cloud.google.com/) → create/select a project.
2. **APIs & Services → Library** → enable **Gmail API**, **Google Calendar API**, **Tasks API**.
3. **OAuth consent screen** → External → add your email as a test user (keeps the app in "Testing" mode — see Limitations for what this caps).
4. **Credentials → Create Credentials → OAuth client ID** → Web application.
   - Local redirect URI: `http://localhost:8000/api/auth/callback`
   - Production redirect URI: `https://<your-domain>/api/auth/callback` (add once deployed; both can coexist)
5. Copy the **Client ID** and **Client Secret**.

### 2. Supabase

1. Create a project at [supabase.com](https://supabase.com).
2. Run `backend/supabase_schema.sql` in the SQL editor.
3. Copy the **Project URL** and **service_role key** (Settings → API).

### 3. Groq

1. Create an API key at [console.groq.com](https://console.groq.com).

### 4. Backend (local dev)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows (Git Bash): source venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env
# fill in: GOOGLE_CLIENT_ID/SECRET, SUPABASE_URL/SERVICE_ROLE_KEY,
#          GROQ_API_KEY, APP_SECRET_KEY, TOKEN_ENCRYPTION_KEY
# GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
# FRONTEND_URL=http://localhost:5173
# generate TOKEN_ENCRYPTION_KEY with:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

uvicorn app.main:app --reload --port 8000
```

### 5. Frontend (local dev)

```bash
cd frontend
npm install
cp .env.example .env    # VITE_API_URL=http://localhost:8000/api
npm run dev
```

### 6. Verify end-to-end (local)

1. Open `http://localhost:5173` → **Continue with Google** → grant access → land on `/dashboard`.
2. Check Supabase: a row in `users`, a row in `oauth_tokens` with ciphertext (not readable JWTs) in the token columns.
3. Go to **Chat**, send *"what's on my calendar today?"* — confirms the agent, tool wiring, and live Google data all work together.
4. Ask it to *"draft an email to test@example.com saying hi"* → check Gmail **Drafts** (not Sent) to confirm the constraint holds in practice, not just in theory.

---

## Deployment

Deployed as a **single Vercel project** — one domain serves the built React
app and the Python backend together, avoiding CORS and cross-origin cookie
issues entirely.

**Key files at the repo root** (not inside `backend/` or `frontend/`):

- `api/index.py` — the Vercel Python function entrypoint. Adds `backend/`
  to `sys.path` and imports the real app from `backend/app/main.py`.
- `requirements.txt` — one line, `-r backend/requirements.txt`, so Vercel's
  Python builder (which looks for `requirements.txt` near the entrypoint)
  finds and installs the real dependency list.
- `.python-version` — pins Python 3.14.
- `vercel.json`:
  ```json
  {
    "buildCommand": "cd frontend && npm install && npm run build",
    "outputDirectory": "frontend/dist",
    "functions": {
      "api/index.py": { "includeFiles": "backend/**" }
    },
    "rewrites": [
      { "source": "/api/(.*)", "destination": "/api" },
      { "source": "/((?!api/).*)", "destination": "/index.html" }
    ]
  }
  ```
  `includeFiles` bundles the entire `backend/` directory alongside the
  function so its imports resolve; the two rewrites send `/api/*` to the
  Python function and everything else to the SPA (with client-side routing
  handled by `index.html`, so refreshing on `/dashboard` or `/chat` works).

**Environment variables**, set in the Vercel project dashboard:

| Variable | Value |
|---|---|
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | from Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `https://<your-domain>/api/auth/callback` |
| `FRONTEND_URL` | `https://<your-domain>` (bare — no `/api`) |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | from Supabase |
| `GROQ_API_KEY` | from Groq console |
| `APP_SECRET_KEY` / `TOKEN_ENCRYPTION_KEY` | generate fresh values for prod, don't reuse local ones |
| `VITE_API_URL` | `/api` (relative — same-origin, domain-independent) |

Env var changes require a redeploy to take effect — they don't apply
retroactively to an already-built deployment.

**Windows-specific gotcha we hit repeatedly:** PowerShell's
`Out-File -Encoding utf8` silently prepends a UTF-8 BOM, which breaks
`requirements.txt` parsing with a cryptic position-0 error. Use
`[System.IO.File]::WriteAllText(path, content, (New-Object System.Text.UTF8Encoding $false))`
instead when creating/editing plain-text config files from PowerShell.

---

## API reference

All paths below are prefixed with `/api` in the actual deployment
(e.g. `/api/auth/login`, `/api/chat`).

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

Full interactive docs at `http://localhost:8000/docs` in local dev.

---

## Security design

- **Session cookie, not JWT-in-localStorage.** A signed, httpOnly cookie holds only an internal `user_id`. It is never readable by client-side JS, which rules out XSS-based session theft.
- **Google tokens never reach the browser.** They're encrypted with Fernet and stored server-side in Supabase; decrypted only in-memory, per-request, inside `get_authed_user`.
- **Least-privilege OAuth scopes.** `gmail.compose` rather than `gmail.modify`/`mail.google.com` — draft-only is a scope-level guarantee, not just a prompt instruction.
- **No send-capable tool exists in code.** Even a successful prompt-injection or model hallucination has no reachable send function to call — the capability was never wired in, not merely discouraged.
- **Auto-refresh with re-persistence.** Expired access tokens are refreshed transparently per-request and the new token is re-encrypted and written back to Supabase.
- **`/api` route prefix.** Prevents any backend route from ever being shadowed by a frontend route of the same name (or vice versa) now that both share one domain.

---

## Limitations (current state)

- **Google OAuth "Testing" mode** — capped at 100 test users and requires each tester's email to be added manually in Cloud Console. Moving to production requires Google's app verification process (not yet done).
- **Single LLM provider, no fallback.** If Groq has an outage or rate-limits the app, `/chat` fails outright — there's no fallback provider or retry/backoff logic yet.
- **No streaming responses.** The agent's full reply is generated before anything is sent to the frontend — no token-by-token streaming, so longer multi-tool responses feel slower than they need to.
- **Sidebar doesn't auto-refresh after chat actions.** If you ask the agent to create a task, the Tasks panel won't reflect it until it's manually reloaded — there's no shared state or event bus between the chat and sidebar yet.
- **Conversation history has no trimming/summarization.** Every prior message in a conversation is loaded and sent to the LLM on every turn — long conversations will eventually hit context-window and cost limits with no graceful degradation.
- **Tasks are limited to the default list (`@default`).** Multiple Google Task lists aren't supported.
- **Update endpoints accept a loosely-typed `dict`.** `PATCH /events/{id}` and `PATCH /todos/{id}` (and the agent's equivalent tools) take a free-form `updates` object rather than a strictly validated schema.
- **Row Level Security is enabled but unused.** Supabase tables have RLS turned on, but the backend uses the service-role key (bypasses RLS) for everything — access control is enforced entirely in application code.
- **No automated tests.** Everything so far has been verified by manual testing against a live Google account and live Vercel deployment logs.
- **No observability into agent decisions.** No tracing (e.g. LangSmith) showing which tools the agent considered or why.
- **Cold-start latency on `/chat`.** A serverless cold start that has to import LangGraph/LangChain/Groq, then make an LLM call and a Google API call, can be noticeably slower than a warm request — not yet profiled or optimized.

---

## Roadmap / planned improvements

- [ ] Stream `/chat` responses (Server-Sent Events or WebSocket) for real-time token output.
- [ ] Push sidebar refresh after any chat turn that used a calendar/task tool.
- [ ] Message history trimming/summarization once a conversation exceeds a token budget.
- [ ] Strict Pydantic schemas for event/task updates instead of free-form `dict`.
- [ ] Move Supabase access to per-user JWTs + real RLS policies, retiring the service-role key from request-time code paths.
- [ ] Add retry/backoff for transient Google API errors (429/5xx) in the service layer.
- [ ] Add an eval/test suite: unit tests for services, integration tests for routers, and behavioral tests for the agent (e.g. "never produces a send action regardless of prompt").
- [ ] Tracing/observability for agent tool-selection (LangSmith or equivalent).
- [ ] Support multiple Google Task lists, not just `@default`.
- [ ] Google app verification to exit OAuth "Testing" mode and remove the 100-user cap.
- [ ] Optional secondary LLM provider as a fallback if Groq is unavailable.
- [ ] Profile and reduce `/chat` cold-start latency (e.g. lazy imports, smaller dependency footprint).

---

## Design decisions worth knowing about

- **Tools are rebuilt per request, not once at startup.** `build_agent(credentials)` constructs fresh Google API clients and binds them into new tool closures on every `/chat` call. This costs a small amount of latency but is what guarantees one user's request can never reach another user's mailbox, calendar, or tasks — there is no shared/global agent object holding anyone's credentials.
- **Service functions are the single source of truth.** `gmail_service.py`, `calendar_service.py`, and `tasks_service.py` are called by both the REST routers *and* the agent's tools — so there is exactly one code path per Google operation, not two implementations that could drift apart.
- **`gmail_service.py` contains no send function, period.** This isn't a disabled/commented-out function — the capability doesn't exist in the codebase at all, which is a stronger guarantee than any runtime check could be.
- **All tool outputs are `json.dumps`'d strings, never raw Python objects.** Some LLM providers reject a tool message whose content is an empty list (a natural result of "no events found"). Returning a JSON string unconditionally — even `"[]"` — avoids this entire class of bug and gives the LLM consistently parseable output.
- **The Vercel entrypoint lives at the repo root, not inside `backend/`.** This was a deliberate restructuring to match Vercel's documented `functions` + `includeFiles` pattern for monorepos, after the earlier legacy `builds`/`routes` config proved unreliable for bundling a static frontend build alongside a Python function in one project.