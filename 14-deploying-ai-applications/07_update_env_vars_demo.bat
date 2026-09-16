@echo off
REM Topic 7 - Change config on already-deployed services, no rebuild needed.
REM Requires: 00_setup_vars.bat already run, both services deployed.

echo == updating news-summarizer's TELEGRAM_CHAT_ID live ==
echo (Replace NEW_CHAT_ID below with a real value to actually change anything)
gcloud run services update %SUMMARIZER_SERVICE_NAME% ^
  --region=%REGION% ^
  --update-env-vars=TELEGRAM_CHAT_ID=NEW_CHAT_ID

echo.
echo == updating news-fetcher's RSS_FEED_URL live ==
gcloud functions deploy %FETCHER_FUNCTION_NAME% ^
  --gen2 --region=%REGION% ^
  --update-env-vars=RSS_FEED_URL=https://news.google.com/rss/search?q=cloud+computing

echo.
echo Notice: no "docker build", no "docker push", no new image anywhere
echo above - just new configuration, live within seconds.
