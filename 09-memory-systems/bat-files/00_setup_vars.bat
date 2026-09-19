@echo off
REM Shared variables for the .bat provisioning scripts in this module
REM (04a_provision_redis_and_bastion.bat, 06a_provision_cloud_sql.bat, 99_cleanup.bat).
REM Run this FIRST, in the SAME Command Prompt window you'll run those in.
REM Keep these values in sync with .env — Python scripts read .env, these
REM .bat scripts read this file, but they should describe the same resources.

set PROJECT_ID=agentic-ai-capstone-1
set REGION=us-central1
set ZONE=us-central1-a

set REDIS_INSTANCE_NAME=agent-memory-redis
set BASTION_VM_NAME=agent-memory-bastion

set CLOUD_SQL_INSTANCE_NAME=agent-memory-sql
set CLOUD_SQL_DB_NAME=memory_db
set CLOUD_SQL_USER=postgres
set CLOUD_SQL_PASSWORD=changeme123

echo Loaded vars: PROJECT_ID=%PROJECT_ID%, REGION=%REGION%, ZONE=%ZONE%
