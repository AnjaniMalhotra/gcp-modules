# Code — Module 15: Event-Driven AI Applications

One small worker (`digest_worker/`), deployed three different ways (`digest-worker-pubsub`, `digest-worker-storage`, `digest-worker-http`), triggered five different ways across this module's topics. **Directly continues Module 14's Daily News Digest Bot** — rebuilt fresh here per the course's isolation rule, but the same story.

## Setup (do this once)

```bat
copy .env.example .env
REM ...fill in real values, including your Telegram bot token and chat ID
pip install -r requirements.txt
gcloud auth application-default login
00_setup_vars.bat
00a_initial_setup.bat
```

## Files

| File / Folder | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Every config key this module needs |
| `00_setup_vars.bat` | — | Config for every other `.bat` script |
| `00a_initial_setup.bat` | — | Service accounts + the Telegram secret, created once upfront |
| `digest_worker/` | — | The shared function source: `main.py` (3 entry points), `requirements.txt` |
| `01_pubsub_setup.bat` | 1 | Create the topic, deploy `digest-worker-pubsub`, publish a test message |
| `02_eventarc_setup.bat` | 2 | Create the bucket, deploy `digest-worker-storage`, upload a test file |
| `03_cloud_scheduler_setup.bat` | 3 | A daily job targeting topic 1's Pub/Sub topic |
| `04_cloud_tasks_setup.bat` | 4 | Queue + `digest-worker-http` deploy + IAM binding |
| `04_create_tasks.py` | 4 | Enqueues one Cloud Task per feed, with an OIDC token attached |
| `05_openapi_spec.yaml` | 5 | The API Gateway config — edit in the real function URL before deploying |
| `05_api_gateway_setup.bat` | 5 | Deploys the API, config, gateway, and an API key |
| `99_cleanup.bat` | — | Tears everything down — good hygiene, even though it's all free-tier |

## How to run these — order matters

1. `00_setup_vars.bat`, then `00a_initial_setup.bat`
2. `01_pubsub_setup.bat` (topic 1)
3. `02_eventarc_setup.bat` (topic 2)
4. `03_cloud_scheduler_setup.bat` (topic 3) — reuses topic 1's Pub/Sub topic, no new function
5. `04_cloud_tasks_setup.bat` (topic 4) — **copy the printed function URL into `.env`/`00_setup_vars.bat` as `WORKER_HTTP_URL`**, then `python 04_create_tasks.py`
6. Edit `05_openapi_spec.yaml`, replacing `WORKER_HTTP_URL_HERE` with the same URL from step 5, then `05_api_gateway_setup.bat` (topic 5)
7. `99_cleanup.bat` when you're done with the module

## Cost note

Pub/Sub (10 GiB/month free), Cloud Scheduler (3 free jobs/month per billing account), Cloud Tasks (1 million free operations/month), and API Gateway (2 million free calls/month) all comfortably cover this module. Eventarc has no separate charge beyond its Pub/Sub transport layer. Same free-tier-friendly profile as Module 14 — no provision/teardown cost discipline needed, though `99_cleanup.bat` is still good practice.
