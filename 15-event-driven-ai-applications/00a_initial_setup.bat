@echo off
REM One-time setup: service accounts + the Telegram secret.
REM Run this once, before any topic's deploy script.
REM Requires: 00_setup_vars.bat already run in this same window.

echo == creating the worker's runtime service account ==
gcloud iam service-accounts create %WORKER_SA_NAME% ^
  --display-name="Digest Worker Runtime SA"

echo == creating the service account Cloud Tasks will use to dispatch tasks ==
gcloud iam service-accounts create %TASKS_SA_NAME% ^
  --display-name="Digest Tasks Dispatcher SA"

echo == creating the Telegram bot token secret ==
gcloud secrets create %SECRET_NAME% --replication-policy=automatic
echo %TELEGRAM_BOT_TOKEN% | gcloud secrets versions add %SECRET_NAME% --data-file=-

echo == letting the worker read that secret ==
gcloud secrets add-iam-policy-binding %SECRET_NAME% ^
  --member="serviceAccount:%WORKER_SA_EMAIL%" ^
  --role="roles/secretmanager.secretAccessor"

echo.
echo Setup complete. Same least-privilege pattern as Module 14 - each
echo service account only has exactly what it needs so far.
