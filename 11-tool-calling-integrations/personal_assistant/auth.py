"""OAuth 2.0 credential handling for Gmail + Calendar (topic 3).

First run: no token.json exists yet, so this opens a browser for the
one-time consent screen. Every run after that: loads token.json and
refreshes silently, no browser needed.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from personal_assistant import config


def get_credentials() -> Credentials:
    creds = None

    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRET_FILE, config.SCOPES)
            creds = flow.run_local_server(port=0)

        with open(config.TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds
