@echo off
REM Shared variables for every .bat script in this module.
REM Run this FIRST, in the SAME Command Prompt window you'll run the rest in.

set PROJECT_ID=agentic-ai-capstone-1
set REGION=us-central1
set LOCATION=us-central1

set REPO_NAME=deploying-ai-apps
set SUMMARIZER_SERVICE_NAME=news-summarizer
set FETCHER_FUNCTION_NAME=news-fetcher

set SUMMARIZER_SA_NAME=news-summarizer-sa
set FETCHER_SA_NAME=news-fetcher-sa
set SUMMARIZER_SA_EMAIL=%SUMMARIZER_SA_NAME%@%PROJECT_ID%.iam.gserviceaccount.com
set FETCHER_SA_EMAIL=%FETCHER_SA_NAME%@%PROJECT_ID%.iam.gserviceaccount.com

set SECRET_NAME=telegram-bot-token

REM DUMMY VALUES - replace with your real Telegram bot details (see topic 5)
set TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
set TELEGRAM_CHAT_ID=your-telegram-chat-id-here

set RSS_FEED_URL=https://news.google.com/rss/search?q=artificial+intelligence

REM Filled in AFTER topic 3's deploy - paste the printed Cloud Run service URL here
set SUMMARIZER_URL=https://REPLACE-ME-AFTER-TOPIC-3.run.app

echo Loaded vars: PROJECT_ID=%PROJECT_ID%, REGION=%REGION%
