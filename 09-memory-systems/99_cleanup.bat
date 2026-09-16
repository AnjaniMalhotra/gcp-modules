@echo off
REM Tears down every billable resource this module provisioned.
REM Requires: 00_setup_vars.bat already run in this same window.
REM Run this at the END of every session using this module - Redis and
REM Cloud SQL both bill hourly, with no free tier, for as long as they exist.

echo == deleting the Cloud SQL instance ==
gcloud sql instances delete %CLOUD_SQL_INSTANCE_NAME% --quiet

echo == deleting the Redis instance ==
gcloud redis instances delete %REDIS_INSTANCE_NAME% --region=%REGION% --quiet

echo == deleting the bastion VM ==
gcloud compute instances delete %BASTION_VM_NAME% --zone=%ZONE% --quiet

echo.
echo All done. If the SSH tunnel window from topic 4 is still open, close it
echo now (Ctrl+C) - it has nothing left to tunnel to.
echo Firestore data is left as-is on purpose - it's free at this scale and
echo needs no cleanup.
