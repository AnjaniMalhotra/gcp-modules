# Code — Module 9: SupportBot Edition

The main track of Module 9: the 8 memory topics taught through one scenario, **SupportBot**, an AI customer support agent handling a messy, multi-day customer interaction. The generic `.py` versions of the same lessons are parked in [`../deleteds/`](../deleteds/README.md) and are not needed.

## Reuses the parent folder's config and infrastructure

- `.env` is read from the **parent** folder (`../.env`), from wherever you run: same `PROJECT_ID`, same Redis instance, same Cloud SQL instance.
- Table, collection and key names are deliberately different from the generic lessons', so both can coexist in one project:

| | Generic lessons (parked) | SupportBot |
|---|---|---|
| Firestore collection | `long_term_memory` | `support_customer_profiles` |
| Cloud SQL tables | `memories` | `support_customers`, `support_tickets` |
| Redis key prefix | `session:` | `support_session:` |

## Setup

Assumes the parent folder's setup is done (`.env` filled in, `pip install -r ../requirements.txt`, `gcloud auth application-default login`, and the infrastructure from [`../commands.md`](../commands.md) for topics 4 to 8).

```bash
../.venv/bin/python setup.py     # prints "setup OK"
```

## Files

| File | Topic | SupportBot use case | Needs |
|------|-------|---------------------|-------|
| `setup.py` | — | Loads `../.env`, builds the Gemini and Firestore clients, reads the Redis host and port | — |
| `01_short_term_memory.ipynb` | 1 | The current live chat: "it keeps crashing" needs the last few messages | nothing |
| `02_long_term_memory.ipynb` | 2 | Remembering a returning customer's plan tier and history | nothing |
| `03_semantic_memory.ipynb` | 3 | Finding a similar past-resolved ticket by meaning | Vertex AI embeddings |
| `04_redis_memory.ipynb` | 4 | Live chat session state, with a TTL | Redis + SSH tunnel |
| `05_firestore_memory.ipynb` | 5 | The durable customer profile | Firestore database |
| `06_cloud_sql_memory.ipynb` | 6 | Structured ticket history, a real JOIN computing average resolution time | Cloud SQL |
| `07_hybrid_memory.ipynb` | 7 | Live session + known profile combined into one context | Redis + Firestore |
| `08_conversation_memory.ipynb` | 8 | Capstone: the `SupportAgentMemory` class, then a real Gemini call that uses it | Redis + Firestore + Gemini |

## How to run these

Start Cloud SQL and Redis first (`../commands.md`): they take a few minutes, sometimes far longer. While they provision, run notebooks 1, 2, 3 and 5. Then open the SSH tunnel and run 4, 7 and 8, and run 6 once Cloud SQL is ready. When you finish, run the teardown commands at the end of `../commands.md`: Redis and Cloud SQL bill hourly.

**Redis port.** The notebooks connect to `REDIS_HOST`:`REDIS_PORT` from `.env` (default `localhost:6379`). If a local Redis already owns 6379, tunnel to another port such as 6380 and set `REDIS_PORT=6380`.

**Files these notebooks write.** Notebook 2 writes `support_customer_facts.json` next to itself. It is gitignored.
