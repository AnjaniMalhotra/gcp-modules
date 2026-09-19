# Code — Module 11: Tool Calling & Integrations — Personal Assistant Agent

One agent (Gemini on Vertex AI, wired up with LangChain) with seven real tools across Gmail, Calendar and Maps. The runnable project is `main.py` + the `personal_assistant/` package; the seven lessons are in `docs/`. The original one-script-per-topic demos are parked in [`deleteds/`](deleteds/README.md) because the project doesn't need them.

**Fully self-contained** — no imports from `code/10-rag-engineering/`.

## Layout

```
11-tool-calling-integrations/
├── main.py                          run the assistant: demo, --chat, or one question
├── 03_google_apis_oauth_setup.py    one-time Google login, creates the token file
├── personal_assistant/              the project code
│   ├── config.py                    settings, reads .env
│   ├── auth.py                      OAuth login (topic 3), used by Gmail + Calendar
│   ├── gmail_tool.py                send_email / read_recent_emails (topic 4)
│   ├── calendar_tool.py             check_availability / create_event (topic 5), list_events
│   ├── maps_tool.py                 get_address_details / get_directions (topic 6)
│   ├── llm.py                       Vertex AI Gemini
│   ├── agent.py                     one agent, all seven tools
│   └── pipeline.py                  build_assistant(), ask(), chat_turn()
├── docs/                            the seven lessons, plus overview and teacher plan
├── deleteds/                        parked lesson demo scripts (see its README)
├── commands.md                      every gcloud command run, with real values
├── requirements.txt
└── .env.example
```

## Setup (do this once)

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
   # ...browser opens, click Allow, the token file gets created
   ```

This module has no `.bat` files: it provisions no infrastructure, only APIs, an API key, and an OAuth consent.

### Dummy values you must replace

Every placeholder is marked in `.env.example` with a `# DUMMY VALUE` comment:

| Key | What to put there |
|-----|--------------------|
| `MAPS_API_KEY` | Your real Maps Platform API key (restricted to Geocoding + Directions) |
| `TEST_EMAIL_ADDRESS` | A real address **you control**. The assistant emails this address, never a real contact |

`client_secret.json` and the token file are **files**, not `.env` values. Both are gitignored; never commit either. Using more than one Google account? Set `TOKEN_FILE` (see `commands.md`) so each account keeps its own login.

## Try it

**Talk to it.** This is the easiest way to test: ask about your plans, your email, or directions, and it remembers the conversation so follow-ups work.

```bash
./.venv/bin/python main.py --chat
```

```
You: What are my plans for the next 24 hours?
You: Am I free tomorrow at 3pm?
You: How long is the drive from Delhi to Agra?
You: quit
```

Or ask a single question and exit:

```bash
./.venv/bin/python main.py "What are my plans for the next 24 hours?"
```

Good things to try:

| Ask | Tool it should use | Changes anything? |
|---|---|---|
| "What are my plans for the next 2 days?" | `list_events` | No |
| "Am I free in 2 hours?" | `check_availability` | No |
| "Show my 3 most recent emails" | `read_recent_emails` | No, but it prints your inbox snippets |
| "Address of the Taj Mahal" / "drive from Delhi to Agra" | Maps tools | No |
| "Book a 30 minute meeting in 3 hours" | `check_availability`, then `create_event` | **Yes: creates a real event** |
| "Email me that it's booked" | `send_email` | **Yes: sends a real email** |

Check Google Calendar and Gmail (Sent) afterwards for anything you asked it to create or send.

**The fixed demo.** `./.venv/bin/python main.py` with no arguments runs three set questions; the third books an event 3 hours out and emails `TEST_EMAIL_ADDRESS`. Run it twice within 3 hours and the second run correctly says you're busy, because the first run's event is in the way.

**Testing one piece at a time, with no side effects:**

```bash
# Smoke test: .env is filled in and Vertex AI works. Prints "setup OK"
./.venv/bin/python -W ignore -c "from personal_assistant.llm import get_llm; print(get_llm().invoke('Reply with exactly: setup OK').text)"

# Maps tool on its own (API key, no login needed)
./.venv/bin/python -W ignore -c "from personal_assistant.maps_tool import get_directions; print(get_directions.invoke({'origin': 'Golden Gate Bridge, San Francisco, CA', 'destination': \"Fisherman's Wharf, San Francisco, CA\", 'mode': 'walking'}))"

# Your calendar on its own, read-only (uses your Google login)
./.venv/bin/python -W ignore -c "from personal_assistant.calendar_tool import list_events; print(list_events.invoke({'days': 2}))"
```

The lesson demos that used to sit next to `main.py` are in `deleteds/` and still run: see its README.

## Note on scope: no multi-agent here

This module deliberately ends with **one agent, seven tools** — not a multi-agent system. Splitting this into a Gmail agent + Calendar agent + Maps agent with a supervisor is saved for the LangGraph module, which is purpose-built for that pattern.
