@echo off
REM Topic 5 - Metrics: view the custom metric the app writes itself.
REM Requires: a few normal (non-error) requests already sent, so there's
REM at least one data point.

echo == sending a normal request to generate a data point ==
echo Run this manually, replacing SERVICE_URL with your real service URL:
echo   curl SERVICE_URL

echo.
echo == querying the custom metric directly ==
gcloud monitoring time-series list ^
  --filter="metric.type=\"custom.googleapis.com/digest/headlines_processed\"" ^
  --format=json

echo.
echo Also viewable in Console -^> Monitoring -^> Metrics Explorer, searching
echo for "headlines_processed" - notice it's NOT in topic 2's built-in list.
