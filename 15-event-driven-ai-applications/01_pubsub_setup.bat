@echo off
REM Topic 1 - Pub/Sub: create the topic, deploy digest-worker-pubsub, test it.
REM Requires: 00_setup_vars.bat + 00a_initial_setup.bat already run.

echo == creating the Pub/Sub topic ==
gcloud pubsub topics create %TOPIC_NAME%

echo == deploying digest-worker-pubsub ==
gcloud functions deploy digest-worker-pubsub ^
  --gen2 --runtime=python311 --region=%REGION% --source=digest_worker ^
  --entry-point=on_pubsub_message ^
  --trigger-topic=%TOPIC_NAME% ^
  --service-account=%WORKER_SA_EMAIL% ^
  --set-env-vars=PROJECT_ID=%PROJECT_ID%,LOCATION=%LOCATION%,TELEGRAM_CHAT_ID=%TELEGRAM_CHAT_ID%,SECRET_NAME=%SECRET_NAME%

echo.
echo == publishing a test message ==
gcloud pubsub topics publish %TOPIC_NAME% --message="{\"feed_url\": \"https://news.google.com/rss/search?q=artificial+intelligence\"}"

echo.
echo Check your Telegram in a few seconds. Also check logs if nothing arrives:
echo   gcloud functions logs read digest-worker-pubsub --region=%REGION% --gen2 --limit=20
