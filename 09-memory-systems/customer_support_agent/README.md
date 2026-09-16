# Code — Module 9 (Updated): SupportBot Edition

A second, use-case-driven pass over Module 9's 8 topics. **The original `.py` files one level up (`../01_short_term_memory.py` through `../08_conversation_memory.py`) are untouched and kept for backup/reference** — this folder doesn't replace them, it teaches the same 8 concepts from scratch through one coherent scenario: **SupportBot**, an AI customer support agent handling a real, messy, multi-day customer interaction.

## Reuses the parent folder's config and infrastructure — provisions nothing new

- `.env` is read from the **parent** folder (`../.env`) — same `PROJECT_ID`, same Redis instance, same Cloud SQL instance. Nothing new to provision, nothing extra to pay for.
- Table/collection/key names are deliberately different from the originals so both scenarios' data can coexist in the same project:

| | Original Module 9 | SupportBot |
|---|---|---|
| Firestore collection | `long_term_memory` | `support_customer_profiles` |
| Cloud SQL tables | `memories` | `support_customers`, `support_tickets` |
| Redis key prefix | `session:` | `support_session:` |

## Setup

Assumes the parent folder's setup is already done (`.env` filled in, `pip install -r ../requirements.txt`, `gcloud auth application-default login`).

```bat
cd customer_support_agent
python 00_setup.py
```

## Files

| File | Matches Doc Topic | SupportBot use case |
|------|--------------------|------------------------|
| `00_setup.py` | — | Loads `../.env`, builds the shared Gemini + Firestore clients |
| `01_short_term_memory.ipynb` | 1 | The current live chat — "it keeps crashing" needs the last few messages |
| `02_long_term_memory.ipynb` | 2 | Remembering a returning customer's plan tier and history |
| `03_semantic_memory.ipynb` | 3 | Finding a similar past-resolved ticket by meaning |
| `04_redis_memory.ipynb` | 4 | Live chat session state (needs `../04a_provision_redis_and_bastion.bat` + the SSH tunnel) |
| `05_firestore_memory.ipynb` | 5 | The durable customer profile |
| `06_cloud_sql_memory.ipynb` | 6 | Structured ticket history (needs `../06a_provision_cloud_sql.bat`) — a real JOIN computing average resolution time |
| `07_hybrid_memory.ipynb` | 7 | Live session + known profile combined into one context |
| `08_conversation_memory.ipynb` | 8 | Capstone — the `SupportAgentMemory` class |

## How to run these

Same infrastructure sequencing as the original module: provisioning (`../04a_provision_redis_and_bastion.bat`, `../06a_provision_cloud_sql.bat`) happens once, from the **parent** folder, before topics 4/6/7/8 here. When done, `../99_cleanup.bat` tears down the same shared infrastructure — run it once, it covers both scenarios' data on that infra.

Notebooks 1, 2, 3, 5 need no infrastructure and can run any time `.env` is filled in.
