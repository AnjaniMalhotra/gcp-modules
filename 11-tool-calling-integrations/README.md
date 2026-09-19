# Code — Module 11: Tool Calling & Integrations — Personal Assistant Agent

One numbered file per topic (all runnable standalone), plus a `personal_assistant/` package for the final combined agent — same "concept files + one real project" shape as Module 9, same LangChain/package pattern as Module 10.

**Fully self-contained** — no imports from `code/10-rag-engineering/`.

## Setup (do this once) — READ THIS FULLY BEFORE RUNNING ANYTHING

[`commands.md`](commands.md) has every `gcloud` command for this module, with real values. Only the OAuth consent screen and client ID can't be done from the CLI.

1. **Enable the APIs and create the Maps key** with the commands in `commands.md` (Gmail, Calendar, Geocoding, Directions, API Keys; the key is restricted to Geocoding + Directions).
2. **Do the one-time OAuth Console setup** in `docs/03-google-apis.md` (consent screen, Desktop OAuth client, download `client_secret.json` into this folder). There's no CLI shortcut for this part.
3. Then:
   ```bash
   cp .env.example .env
   # ...replace every DUMMY VALUE in .env with a real one
   python3 -m venv .venv
   ./.venv/bin/pip install -r requirements.txt
   ./.venv/bin/python 03_google_apis_oauth_setup.py
   # ...browser opens, click Allow, token.json gets created
   ./.venv/bin/python 00_setup.py
   ```

(This module has no `.bat` files: it provisions no infrastructure, only APIs, an API key, and an OAuth consent.)

## Dummy values you must replace

Every placeholder is clearly marked in `.env.example` with a `# DUMMY VALUE` comment:

| Key | What to put there |
|-----|--------------------|
| `MAPS_API_KEY` | Your real Maps Platform API key (restricted to Geocoding + Directions) |
| `TEST_EMAIL_ADDRESS` | A real address **you control** — the Gmail demo sends to this, never a real contact |

`client_secret.json` and `token.json` are **files**, not `.env` values — see setup step 1 above. Both are gitignored; never commit either.

## Files

| File | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Config + dummy values clearly marked |
| `requirements.txt` | — | Every Python package this module needs |
| `00_setup.py` | — | Sanity-checks Vertex AI + flags any leftover dummy values |
| `01_function_calling_recap.py` | 1 | Fast recap, nothing new |
| `02_rest_apis.py` | 2 | Generic REST API called as a tool, no auth |
| `03_google_apis_oauth_setup.py` | 3 | **Run this once** — the one-time browser consent flow |
| `04_gmail_tool.py` | 4 | Read + send email |
| `05_calendar_tool.py` | 5 | Check availability + create an event |
| `06_maps_tool.py` | 6 | Geocode + directions (API key, no OAuth) |
| `07_authentication_demo.py` | 7 | All three auth patterns, side by side |
| `personal_assistant/config.py` | — | All settings, reads `.env` |
| `personal_assistant/auth.py` | 3 | Shared OAuth credential loading (used by Gmail + Calendar tools) |
| `personal_assistant/gmail_tool.py` | 4 | `send_email` / `read_recent_emails` as agent tools |
| `personal_assistant/calendar_tool.py` | 5 | `check_availability` / `create_event` as agent tools |
| `personal_assistant/maps_tool.py` | 6 | `get_address_details` / `get_directions` as agent tools |
| `personal_assistant/llm.py` | — | Vertex AI Gemini, same pattern as Module 10 |
| `personal_assistant/agent.py` | — | One agent, all 6 tools |
| `personal_assistant/pipeline.py` | — | Single entry point `main.py` calls |
| `main.py` | — | CLI demo — the combined "check, schedule, email" request |

## How to run these — order matters

1. Complete the Console setup (see above) — one time
2. `python 03_google_apis_oauth_setup.py` — one time, click Allow in the browser
3. Topics 1, 2, 6 can run in any order — no shared state
4. Topics 4, 5, 7 need step 2 done first (they use `token.json`)
5. `python main.py` for the full combined agent

## Note on scope: no multi-agent here

This module deliberately ends with **one agent, six tools** — not a multi-agent system. Splitting this into a Gmail agent + Calendar agent + Maps agent with a supervisor is saved for the LangGraph module, which is purpose-built for that pattern.
