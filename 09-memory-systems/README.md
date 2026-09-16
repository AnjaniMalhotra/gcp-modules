# Code — Module 9: Memory Systems

This module is self-contained (see `.claude/CLAUDE.md` — no cross-module imports) and mixes two formats: `.bat` for provisioning real infrastructure (Redis, Cloud SQL), Python for everything else.

> **A second, use-case-driven pass over these same 8 topics exists at [`customer_support_agent/`](customer_support_agent/README.md)** — Jupyter notebooks teaching the same concepts through one coherent scenario (an AI customer support agent), reusing this folder's infrastructure. These `.py` files are kept as-is for backup/reference, not replaced.

## Setup (do this once)

```bat
copy .env.example .env
REM ...then edit .env with your real PROJECT_ID and a real CLOUD_SQL_PASSWORD
pip install -r requirements.txt
00_setup_vars.bat
python 00_setup.py
```
`00_setup.py` should print `setup OK`. Keep `.env` and `00_setup_vars.bat` describing the *same* resources — they're read by Python and `.bat` scripts respectively.

## Files

| File | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Every config key this module needs, including the first real secret (`CLOUD_SQL_PASSWORD`) |
| `requirements.txt` | — | Python packages this module needs |
| `00_setup_vars.bat` | — | Config for the `.bat` provisioning scripts |
| `00_setup.py` | — | Loads `.env`, builds the shared Gemini + Firestore clients |
| `01_short_term_memory.py` | 1 | Sliding-window in-process memory |
| `02_long_term_memory.py` | 2 | Persisting memory to a local file |
| `03_semantic_memory.py` | 3 | Embeddings-based recall, written fresh (no import from Module 3) |
| `04a_provision_redis_and_bastion.bat` | 4 | Creates Memorystore Redis + a bastion VM |
| `04_redis_memory.py` | 4 | Redis demo, run through the SSH tunnel |
| `05_firestore_memory.py` | 5 | Firestore demo — no provisioning needed |
| `06a_provision_cloud_sql.bat` | 6 | Creates the Cloud SQL Postgres instance — **start this during topic 4**, it's slow |
| `06_cloud_sql_memory.py` | 6 | Cloud SQL demo via the Python Connector — no bastion needed |
| `07_hybrid_memory.py` | 7 | Redis + Firestore combined |
| `08_conversation_memory.py` | 8 | Capstone: a `ConversationMemory` class wrapping topic 7 |
| `99_cleanup.bat` | — | Deletes every billable resource this module created — **always run this last** |

## How to run these — the order matters here more than in past modules

1. `00_setup_vars.bat` then `04a_provision_redis_and_bastion.bat` (kicks off both Redis and the bastion VM)
2. **Also start `06a_provision_cloud_sql.bat` around now** — Cloud SQL takes 5-10 minutes, so let it run in the background while you work through topics 4 and 5
3. In a **second** Command Prompt window: the SSH tunnel command that `04a` printed — leave this window open and running
4. Back in the first window: `python 01_short_term_memory.py`, `02_...`, `03_...`, `04_redis_memory.py`, `05_firestore_memory.py`
5. By the time you reach topic 6, Cloud SQL should be ready — `python 06_cloud_sql_memory.py`
6. `07_hybrid_memory.py`, `08_conversation_memory.py`
7. **`99_cleanup.bat`** — every time, without exception. Redis and Cloud SQL have no free tier.

## Cost note

Firestore is free at this scale. Memorystore and Cloud SQL are **not** — confirmed against Google's own Always-Free product list (neither appears on it). They bill every hour they exist, trial credit or not. This is the first module in the course where "forgot to clean up" has a real dollar cost attached.
