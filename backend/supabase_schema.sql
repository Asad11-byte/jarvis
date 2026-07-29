-- Run this in the Supabase SQL editor before starting the app.

create extension if not exists "uuid-ossp";

create table if not exists users (
    id uuid primary key default uuid_generate_v4(),
    google_sub text unique not null,      -- Google's stable user id ("sub" claim)
    email text not null,
    full_name text,
    avatar_url text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists oauth_tokens (
    user_id uuid primary key references users(id) on delete cascade,
    access_token_enc text not null,
    refresh_token_enc text,               -- may be null on re-consent; keep old one if so
    scopes text not null,
    expiry timestamptz not null,
    updated_at timestamptz not null default now()
);

create table if not exists conversations (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text,
    created_at timestamptz not null default now()
);

create table if not exists messages (
    id uuid primary key default uuid_generate_v4(),
    conversation_id uuid not null references conversations(id) on delete cascade,
    role text not null,                   -- 'user' | 'assistant' | 'tool'
    content text,
    tool_calls jsonb,
    created_at timestamptz not null default now()
);

-- Row Level Security: enable now, policies added once we wire up
-- per-request Supabase auth (Phase 2+). Service-role key bypasses these,
-- so today the app enforces scoping in code -- this just prevents any
-- future anon-key usage from leaking data.
alter table users enable row level security;
alter table oauth_tokens enable row level security;
alter table conversations enable row level security;
alter table messages enable row level security;
