@echo off
REM Topic 4 - Provision Memorystore Redis + a bastion VM to reach it.
REM Requires: 00_setup_vars.bat already run in this same window.
REM Same pattern as Module 9 - no free tier for either resource,
REM run 99_cleanup.bat when done.

echo == creating the Memorystore Redis instance (Basic tier, 1GB, cheapest option) ==
gcloud redis instances create %REDIS_INSTANCE_NAME% ^
  --size=1 ^
  --region=%REGION% ^
  --tier=basic ^
  --redis-version=redis_7_0

echo == fetching its internal IP - you'll need this for the SSH tunnel below ==
gcloud redis instances describe %REDIS_INSTANCE_NAME% --region=%REGION% --format="value(host)"

echo == creating a tiny bastion VM in the same network (free-tier eligible e2-micro) ==
gcloud compute instances create %BASTION_VM_NAME% ^
  --zone=%ZONE% ^
  --machine-type=e2-micro ^
  --image-family=debian-12 ^
  --image-project=debian-cloud

echo.
echo NEXT STEP - in a SECOND Command Prompt window, run:
echo   gcloud compute ssh %BASTION_VM_NAME% --zone=%ZONE% -- -L 6379:REDIS_IP_FROM_ABOVE:6379 -N
echo Replace REDIS_IP_FROM_ABOVE with the "host" value printed above.
echo Leave that window open and running, then come back to THIS window and
echo run the 04_redis.ipynb notebook.
