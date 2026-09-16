# Code — Module 17: Production AI Engineering

One small, self-contained Flask service — **ModeraAI**, a content moderation API — hardened topic by topic against real production failure modes: bursty traffic, unreliable dependencies, hangs, abuse, and cost blowups. No code imported from any other module, per the isolation rule.

**Scope note:** deployed `--allow-unauthenticated`, same as Module 16, so every topic's `curl`/`load_test.py` call is testable with a plain URL — auth/IAM isn't this module's focus.

## Setup (do this once)

```bat
copy .env.example .env
REM ...fill in real values: your GitHub username (topic 3)
gcloud auth application-default login
pip install -r requirements.txt
00_setup_vars.bat
00a_initial_setup.bat
```

## Files

| File | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Every config key this module needs |
| `00_setup_vars.bat` | — | Config for every other `.bat` script |
| `00a_initial_setup.bat` | — | APIs, Artifact Registry repo, Firestore DB, runtime service account |
| `moderaai/` | — | The service itself: `main.py`, `Dockerfile`, `requirements.txt`, `cloudbuild.yaml` |
| `01_deploy_and_load_test.bat` + `load_test.py` | 1 | Deploy v1, fire 50 concurrent requests, watch instance count scale |
| `02_cloud_build_manual.bat` | 2 | A manual, one-off remote build + push + deploy via `cloudbuild.yaml` |
| `03_create_ci_cd_trigger.bat` | 3 | Creates the push-to-deploy trigger (GitHub connection is a one-time Console step done first) |
| `04_deploy_v2_no_traffic.bat` | 4 | Builds/deploys `v2.0.0` (stricter policy) alongside v1, at 0% traffic |
| `05_rollback_demo.bat` | 5 | Promotes v2, proves it over-flags safe text, rolls back to v1 |
| `06_test_caching_retries_timeouts.bat` | 6, 7, 8 | curl calls demoing caching, the retry switch, and the timeout switch (all built into `main.py`) |
| `09_openapi_spec.yaml` + `09_api_gateway_rate_limit_setup.bat` | 9 | API Gateway with a declarative 10-req/min quota — no hand-rolled rate-limiting code |
| `10_cost_comparison_demo.py` | 10 | Flash vs. Pro token/cost comparison, plus proof caching cuts real Gemini calls |
| `99_cleanup.bat` | — | Tears everything down |

## How to run these — order matters

1. `00_setup_vars.bat`, then `00a_initial_setup.bat`
2. `01_deploy_and_load_test.bat` (topic 1) — **copy the printed service URL into `.env`/`00_setup_vars.bat` as `SERVICE_URL`**
3. `02_cloud_build_manual.bat` (topic 2)
4. Connect GitHub in the Console (Cloud Build → Triggers → Connect Repository), then `03_create_ci_cd_trigger.bat` (topic 3) — test by pushing a real commit
5. `04_deploy_v2_no_traffic.bat` (topic 4)
6. `05_rollback_demo.bat` (topic 5) — **fill in the printed v1 revision name where the script pauses**
7. `06_test_caching_retries_timeouts.bat` (topics 6-8)
8. Edit `09_openapi_spec.yaml` — replace `MODERAAI_SERVICE_URL_HERE` with the real `SERVICE_URL` — then `09_api_gateway_rate_limit_setup.bat` (topic 9) — **copy the printed hostname into `.env`/`00_setup_vars.bat` as `GATEWAY_URL`, and the printed API key as `API_KEY`** (the quota is scoped per calling project, and the API key is how the gateway identifies which project is calling — no key, no enforcement)
9. `python 10_cost_comparison_demo.py` (topic 10)
10. `99_cleanup.bat` when you're done with the module

## Cost note

Cloud Run, Cloud Build (120 free build-minutes/day), Artifact Registry (0.5 GB free), Firestore (1 GiB free storage + generous free daily reads/writes), and API Gateway (2M free calls/month) all comfortably cover this module's teaching load. The only real spend is Gemini calls themselves — kept small by this module's own caching (topic 6) and Flash-by-default model choice. `99_cleanup.bat` is still good practice.
