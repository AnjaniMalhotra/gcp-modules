# Code — Module 14: Deploying AI Applications

Two small services, deployed two different ways, building up piece by piece across the module's 7 topics: **`news-fetcher`** (Cloud Function) calls **`news-summarizer`** (Cloud Run, Docker container), which summarizes headlines with Gemini and sends the result to your personal Telegram.

**The pipeline doesn't fully work until topic 6.** Each earlier topic's test call fails with a specific, informative, expected error — see each `.bat` script's comments and the topic docs for exactly what to expect and why. This is deliberate, not a bug in these instructions.

## Setup (do this once)

1. Install Docker Desktop, make sure it's running
2. Create a Telegram bot via [@BotFather](https://t.me/BotFather), get your token and chat ID (full steps in `docs/05-secret-manager.md`)
3. ```bat
   copy .env.example .env
   REM ...fill in real values, including your Telegram token and chat ID
   gcloud auth application-default login
   00_setup_vars.bat
   00a_create_service_accounts.bat
   ```

## Files

| File / Folder | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Every config key this module needs |
| `00_setup_vars.bat` | — | Config for every other `.bat` script |
| `00a_create_service_accounts.bat` | — | Creates both runtime SAs early, with zero extra roles on purpose |
| `news_summarizer/` | 1 | The Cloud Run service: `main.py`, `Dockerfile`, `requirements.txt` |
| `01_docker_build_and_test_local.bat` | 1 | Build + run the summarizer locally |
| `02_artifact_registry_push.bat` | 2 | Create the repo, push the image |
| `03_deploy_cloud_run.bat` | 3 | Deploy the summarizer — expect a "secret not found" test failure |
| `news_fetcher/` | 4 | The Cloud Function: `main.py`, `requirements.txt` |
| `04_deploy_cloud_function.bat` | 4 | Deploy the fetcher — expect a 403 test failure |
| `05_secret_manager_setup.bat` | 5 | Create the Telegram token secret — the earlier error changes shape |
| `06_iam_setup.bat` | 6 | Grant both IAM bindings — the full pipeline finally works |
| `07_update_env_vars_demo.bat` | 7 | Change config on live services, no rebuild |
| `99_cleanup.bat` | — | Tears everything down — good hygiene, even though it's all free-tier |

## How to run these — order matters, by design

1. `00_setup_vars.bat`, then `00a_create_service_accounts.bat`
2. `01_docker_build_and_test_local.bat` (topic 1)
3. `02_artifact_registry_push.bat` (topic 2)
4. `03_deploy_cloud_run.bat` (topic 3) — **copy the printed service URL into `.env`/`00_setup_vars.bat` as `SUMMARIZER_URL`** before continuing
5. `04_deploy_cloud_function.bat` (topic 4)
6. `05_secret_manager_setup.bat` (topic 5)
7. `06_iam_setup.bat` (topic 6) — this is where it all finally connects
8. `07_update_env_vars_demo.bat` (topic 7)
9. `99_cleanup.bat` when you're done with the module

## Cost note

Cloud Run, Cloud Functions, Artifact Registry, and Secret Manager all have real Always Free allowances that comfortably cover this module's usage — see the module overview doc for the exact numbers. This is the first deployment module in the course that doesn't need Module 9's provision-then-teardown discipline for cost reasons (though `99_cleanup.bat` is still good practice).
