@echo off
REM Creates the two runtime service accounts BOTH deployed services will use.
REM Run this once, early, before topics 3-4's deploys reference them.
REM Requires: 00_setup_vars.bat already run in this same window.
REM
REM NOTE: these accounts are created with NO extra IAM roles yet on purpose -
REM topic 6 grants the actual permissions, so their absence is visible and
REM the "why do I need IAM" lesson lands for real, not abstractly.

echo == creating the news-summarizer runtime service account ==
gcloud iam service-accounts create %SUMMARIZER_SA_NAME% ^
  --display-name="News Summarizer Runtime SA"

echo == creating the news-fetcher runtime service account ==
gcloud iam service-accounts create %FETCHER_SA_NAME% ^
  --display-name="News Fetcher Runtime SA"

echo.
echo Both service accounts created. Neither has any extra IAM roles yet -
echo that's topic 6.
