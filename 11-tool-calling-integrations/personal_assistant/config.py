"""All settings for the app live here, in one place.

Same pattern as Module 10's hr_assistant/config.py.
"""

import os
from dotenv import load_dotenv

load_dotenv()

## GCP / LLM

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
LLM_MODEL_NAME = "gemini-2.5-flash"  # verify still current/GA - see code/03-vertex-ai-gemini/docs/02-gemini-models.md

## MAPS (topic 6 — plain API key, no OAuth)

MAPS_API_KEY = os.getenv("MAPS_API_KEY")

## GMAIL / CALENDAR (topics 3-5 — OAuth, see auth.py)

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")  # one token file per Google account

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]

## MISC

TEST_EMAIL_ADDRESS = os.getenv("TEST_EMAIL_ADDRESS")

SYSTEM_PROMPT = (
    "You are a helpful personal assistant with access to the user's email, "
    "calendar, and maps. Always check calendar availability before creating "
    "an event. Confirm details clearly before sending an email. Be concise."
)


def check_config() -> None:
    """Stop early with a clear message if required config/files are missing."""
    missing = []
    if not PROJECT_ID:
        missing.append("PROJECT_ID")
    if not MAPS_API_KEY or MAPS_API_KEY == "your-maps-api-key-here":
        missing.append("MAPS_API_KEY (still the dummy placeholder value)")
    if not os.path.exists(CLIENT_SECRET_FILE):
        missing.append(f"{CLIENT_SECRET_FILE} (download from Console — see topic 3 docs)")
    if missing:
        raise ValueError(f"Missing/incomplete config: {', '.join(missing)}")
