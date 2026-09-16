@echo off
REM Topic 2 - Eventarc: create the bucket, deploy digest-worker-storage, test it.
REM Requires: 00_setup_vars.bat + 00a_initial_setup.bat already run.

echo == creating the feeds bucket ==
gcloud storage buckets create gs://%FEEDS_BUCKET_NAME% --location=%REGION%

echo == deploying digest-worker-storage (Eventarc-triggered) ==
gcloud functions deploy digest-worker-storage ^
  --gen2 --runtime=python311 --region=%REGION% --source=digest_worker ^
  --entry-point=on_storage_event ^
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" ^
  --trigger-event-filters="bucket=%FEEDS_BUCKET_NAME%" ^
  --service-account=%WORKER_SA_EMAIL% ^
  --set-env-vars=PROJECT_ID=%PROJECT_ID%,LOCATION=%LOCATION%,TELEGRAM_CHAT_ID=%TELEGRAM_CHAT_ID%,SECRET_NAME=%SECRET_NAME%

echo.
echo == uploading a test feeds.txt ==
echo https://news.google.com/rss/search?q=artificial+intelligence > feeds.txt
gcloud storage cp feeds.txt gs://%FEEDS_BUCKET_NAME%/feeds.txt

echo.
echo Check your Telegram in a few seconds - no direct call was made, the
echo upload itself triggered everything. Check logs if nothing arrives:
echo   gcloud functions logs read digest-worker-storage --region=%REGION% --gen2 --limit=20
