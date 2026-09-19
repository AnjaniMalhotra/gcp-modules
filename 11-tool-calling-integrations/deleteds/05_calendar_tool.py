# %% [markdown]
# # Topic 5 — Calendar API
# Requires: 03_google_apis_oauth_setup.py already run once (token.json exists).

# %%
from datetime import datetime, timedelta

from googleapiclient.discovery import build

from personal_assistant.auth import get_credentials

creds = get_credentials()
calendar_service = build("calendar", "v3", credentials=creds)

# %%
# Check free/busy for the next hour
now = datetime.utcnow()
body = {
    "timeMin": now.isoformat() + "Z",
    "timeMax": (now + timedelta(hours=1)).isoformat() + "Z",
    "items": [{"id": "primary"}],
}
freebusy = calendar_service.freebusy().query(body=body).execute()
busy_slots = freebusy["calendars"]["primary"]["busy"]
print("Busy slots:", busy_slots)

# %%
# Only create the event if actually free
if not busy_slots:
    event = {
        "summary": "Team Meeting (Module 11 demo)",
        "start": {"dateTime": now.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": (now + timedelta(minutes=30)).isoformat(), "timeZone": "UTC"},
    }
    created = calendar_service.events().insert(calendarId="primary", body=event).execute()
    print("Created:", created.get("htmlLink"))
else:
    print("Not free — skipping event creation.")
