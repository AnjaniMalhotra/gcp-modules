@echo off
REM Topic 2 - Cloud Monitoring: generate some traffic, then look at the
REM built-in metrics that were collected automatically.
REM Requires: 01_deploy_and_view_logging.bat already run.

echo == sending a few normal requests to generate data ==
echo Run these manually, replacing SERVICE_URL with your real service URL:
echo   curl SERVICE_URL
echo   curl SERVICE_URL
echo   curl SERVICE_URL

echo.
echo == listing available Cloud Run metric types (no code was written for any of these) ==
gcloud monitoring metrics-descriptors list --filter="metric.type:run.googleapis.com" --limit=10

echo.
echo Now open Console -^> Monitoring -^> Metrics Explorer, resource type
echo "Cloud Run Revision", and chart Request Count or Request Latencies.
