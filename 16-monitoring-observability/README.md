# Code — Module 16: Monitoring & Observability

One instrumented Cloud Run service, **rebuilt fresh** from Module 14/15's Daily News Digest idea (no code imports, per the isolation rule) — this time wired with structured logging, custom trace spans, a custom metric, and two switches that deliberately break it: `?simulate_error=true` and `?simulate_slow=true`.

**Scope note:** unlike Module 14, this service is deployed `--allow-unauthenticated` — auth/IAM isn't this module's focus, and removing it keeps every topic's `curl` testable with a plain URL, no identity token boilerplate in the way.

## Setup (do this once)

```bat
copy .env.example .env
REM ...fill in real values: Telegram token/chat ID, and a real NOTIFICATION_EMAIL
gcloud auth application-default login
00_setup_vars.bat
00a_initial_setup.bat
```

## Files

| File | Matches Doc Topic | What It Does |
|------|--------------------|---------------|
| `.env.example` | — | Every config key this module needs |
| `00_setup_vars.bat` | — | Config for every other `.bat` script |
| `00a_initial_setup.bat` | — | Service account + IAM roles to *write* logs/traces/metrics + the Telegram secret |
| `digest_worker_observable/` | — | The instrumented service: `main.py`, `Dockerfile`, `requirements.txt` |
| `01_deploy_and_view_logging.bat` | 1 | Deploy from source, send a request, read structured logs |
| `02_view_monitoring.bat` | 2 | Tour the built-in, automatically-collected metrics |
| `03_trigger_error_reporting.bat` | 3 | Trigger a real crash, watch it get auto-grouped |
| `04_trigger_cloud_trace.bat` | 4 | Trigger deliberate slowness, read the trace waterfall |
| `05_view_custom_metric.bat` | 5 | View the custom metric the app writes itself |
| `06_alert_policy.json` + `06_create_alert.bat` | 6 | Log-based metric + notification channel + alert policy |
| `07_dashboard.json` + `07_create_dashboard.bat` | 7 | One dashboard combining every signal above |
| `99_cleanup.bat` | — | Tears everything down |

## How to run these — order matters

1. `00_setup_vars.bat`, then `00a_initial_setup.bat`
2. `01_deploy_and_view_logging.bat` — **copy the printed service URL into `.env`/`00_setup_vars.bat` as `SERVICE_URL`**
3. `02_view_monitoring.bat` (topic 2)
4. `03_trigger_error_reporting.bat` (topic 3)
5. `04_trigger_cloud_trace.bat` (topic 4)
6. `05_view_custom_metric.bat` (topic 5)
7. `06_create_alert.bat` (topic 6) — **edit `06_alert_policy.json`** with the real notification channel ID it prints before creating the policy
8. `07_create_dashboard.bat` (topic 7)
9. `99_cleanup.bat` when you're done with the module

## Cost note

Cloud Logging (50 GiB/month free), Cloud Monitoring (150 MiB of metrics/month free), Cloud Trace (2.5 million spans/month free), and Error Reporting (free, built on Logging) all comfortably cover this module. No provision/teardown cost discipline needed, though `99_cleanup.bat` is still good practice.
