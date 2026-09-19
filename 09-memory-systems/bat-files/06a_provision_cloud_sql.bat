@echo off
REM Topic 6 - Provision a Cloud SQL for PostgreSQL instance.
REM Requires: 00_setup_vars.bat already run in this same window.
REM IMPORTANT: start this EARLY - during topic 4 - instance creation takes
REM 5-10 minutes. Do not wait on this live; let it run in the background.
REM No free tier - run 99_cleanup.bat when done.

echo == creating the Cloud SQL Postgres instance (smallest practical size) ==
gcloud sql instances create %CLOUD_SQL_INSTANCE_NAME% ^
  --database-version=POSTGRES_15 ^
  --cpu=1 ^
  --memory=3840MB ^
  --region=%REGION% ^
  --storage-size=10GB ^
  --storage-type=SSD ^
  --root-password=%CLOUD_SQL_PASSWORD%

echo == creating the database inside it ==
gcloud sql databases create %CLOUD_SQL_DB_NAME% --instance=%CLOUD_SQL_INSTANCE_NAME%

echo == confirming it's ready (should print RUNNABLE) ==
gcloud sql instances describe %CLOUD_SQL_INSTANCE_NAME% --format="value(state)"
