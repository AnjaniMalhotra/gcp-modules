@echo off
REM Topic 6 - Alerts: log-based metric + notification channel + alert policy.
REM Requires: 00_setup_vars.bat run, NOTIFICATION_EMAIL set to a real address.

echo == creating the log-based metric that counts simulated errors ==
gcloud logging metrics create digest_simulated_errors ^
  --description="Counts simulated digest-worker errors" ^
  --log-filter="resource.type=cloud_run_revision AND textPayload:\"simulated failure triggered on purpose\""

echo.
echo == creating the email notification channel ==
gcloud alpha monitoring channels create ^
  --display-name="My Email" ^
  --type=email ^
  --channel-labels=email_address=%NOTIFICATION_EMAIL%

echo.
echo == IMPORTANT: copy the channel ID printed above ==
echo Open 06_alert_policy.json and replace NOTIFICATION_CHANNEL_ID_HERE with
echo the full channel name (looks like: projects/PROJECT_ID/notificationChannels/1234567890)

echo.
echo Then run:
echo   gcloud alpha monitoring policies create --policy-from-file=06_alert_policy.json

echo.
echo Once the policy exists, trigger it:
echo   curl "SERVICE_URL/?simulate_error=true"
echo   curl "SERVICE_URL/?simulate_error=true"
echo.
echo Then WAIT a minute or two - evaluation and notification both take real time.
