@echo off
REM Shared variables for the .bat provisioning scripts in this module
REM (03a_provision_cloud_sql.bat, 04a_provision_redis_and_bastion.bat, 99_cleanup.bat).
REM Run this FIRST, in the SAME Command Prompt window you'll run those in.
REM Keep these values in sync with .env.

set PROJECT_ID=agentic-ai-capstone-1
set REGION=us-central1
set ZONE=us-central1-a

set GCS_BUCKET_NAME=school-ai-assistant-docs

set CLOUD_SQL_INSTANCE_NAME=school-attendance-sql
set CLOUD_SQL_DB_NAME=school_db
set CLOUD_SQL_USER=postgres
set CLOUD_SQL_PASSWORD=changeme123

set REDIS_INSTANCE_NAME=school-insights-redis
set BASTION_VM_NAME=school-insights-bastion

echo Loaded vars: PROJECT_ID=%PROJECT_ID%, REGION=%REGION%
