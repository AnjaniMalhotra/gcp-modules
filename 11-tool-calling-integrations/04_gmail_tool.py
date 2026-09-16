# %% [markdown]
# # Topic 4 — Gmail API
# Requires: 03_google_apis_oauth_setup.py already run once (token.json exists).

# %%
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from personal_assistant import config
from personal_assistant.auth import get_credentials

creds = get_credentials()
gmail_service = build("gmail", "v1", credentials=creds)

# %%
# Read the 3 most recent messages
results = gmail_service.users().messages().list(userId="me", maxResults=3).execute()
for msg in results.get("messages", []):
    detail = gmail_service.users().messages().get(userId="me", id=msg["id"]).execute()
    print(detail["snippet"])

# %%
# Send a test message — TEST_EMAIL_ADDRESS from .env, not a real contact
message = MIMEText("This is a test email sent by the Personal Assistant Agent.")
message["to"] = config.TEST_EMAIL_ADDRESS
message["subject"] = "Test from Module 11"

encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
gmail_service.users().messages().send(userId="me", body={"raw": encoded}).execute()
print(f"Sent to {config.TEST_EMAIL_ADDRESS}!")
