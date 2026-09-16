# Code — Module 13: Storage for AI Applications

Small, focused Jupyter notebooks — same format as Module 7 — one per topic, all built around a small "School AI Assistant" (except topic 5, which deliberately uses a real public dataset instead). Self-contained: no imports from `code/09-memory-systems/`, even though topics 3-4 reuse patterns taught there.

## Setup (do this once)

```bat
copy .env.example .env
REM ...fill in PROJECT_ID and a real CLOUD_SQL_PASSWORD
pip install -r requirements.txt
gcloud auth application-default login
00_setup_vars.bat
python 00_setup.py
```

## Files

| File | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Every config key this module needs |
| `requirements.txt` | — | Python packages this module needs |
| `00_setup_vars.bat` | — | Config for the `.bat` provisioning scripts |
| `00_setup.py` | — | Loads `.env`, builds the shared Gemini client |
| `01_cloud_storage.ipynb` | 1 | Student Documents Vault — CRUD + signed URL |
| `02_firestore.ipynb` | 2 | Student Profiles — nested fields, arrays, queries |
| `03a_provision_cloud_sql.bat` | 3 | Creates the Cloud SQL Postgres instance — **start this early**, it's slow |
| `03_cloud_sql.ipynb` | 3 | Student Attendance — two related tables, JOIN query |
| `04a_provision_redis_and_bastion.bat` | 4 | Creates Memorystore Redis + a bastion VM |
| `04_redis.ipynb` | 4 | Cached AI Insights — LLM response caching with a TTL |
| `05_bigquery.ipynb` | 5 | Ask Hacker News — public dataset + a small NL-to-SQL agent |
| `06_choosing_the_right_storage.ipynb` | 6 | Comparison table + scenario questions — no new infra |
| `99_cleanup.bat` | — | Deletes every billable resource — **always run this last** |

## How to run these — order matters here

1. `00_setup_vars.bat` then `03a_provision_cloud_sql.bat` (kicks off Cloud SQL — slow, start early)
2. Also start `04a_provision_redis_and_bastion.bat` around now
3. Work through `01_cloud_storage.ipynb` and `02_firestore.ipynb` while both provisioning steps run in the background
4. In a **second** Command Prompt window: the SSH tunnel command `04a` printed — leave it open
5. `03_cloud_sql.ipynb`, then `04_redis.ipynb`
6. `05_bigquery.ipynb` — no provisioning needed, just `.env` filled in
7. `06_choosing_the_right_storage.ipynb`
8. **`99_cleanup.bat`** — every time, without exception. Cloud SQL and Redis have no free tier.

## Cost note

Cloud Storage, Firestore, and BigQuery are free or near-free at this scale (BigQuery: 1 TiB of query processing free every month, and public dataset storage costs nothing at all). Cloud SQL and Redis are **not** free — confirmed against Google's Always-Free list, same as Module 9. Topic 5 also needs *query* discipline, not just cost discipline: `LIMIT` does not reduce bytes scanned — always check a dry run first.
