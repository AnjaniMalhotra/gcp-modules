"""Calendar as an agent tool — wraps topic 5's freebusy + create-event logic."""

from datetime import datetime, timedelta

from googleapiclient.discovery import build
from langchain.tools import tool

from personal_assistant.auth import get_credentials


def _get_calendar_service():
    return build("calendar", "v3", credentials=get_credentials())


@tool
def check_availability(hours_from_now: float, duration_minutes: int = 30) -> str:
    """Check if the user's primary calendar is free starting `hours_from_now`
    hours from the current time, for `duration_minutes` minutes."""
    service = _get_calendar_service()
    start = datetime.utcnow() + timedelta(hours=hours_from_now)
    end = start + timedelta(minutes=duration_minutes)

    body = {
        "timeMin": start.isoformat() + "Z",
        "timeMax": end.isoformat() + "Z",
        "items": [{"id": "primary"}],
    }
    freebusy = service.freebusy().query(body=body).execute()
    busy_slots = freebusy["calendars"]["primary"]["busy"]

    if busy_slots:
        return f"Busy during that time: {busy_slots}"
    return f"Free from {start.isoformat()} to {end.isoformat()} (UTC)."


@tool
def create_event(summary: str, hours_from_now: float, duration_minutes: int = 30) -> str:
    """Create a calendar event. Only call this after confirming the user is
    actually free with check_availability."""
    service = _get_calendar_service()
    start = datetime.utcnow() + timedelta(hours=hours_from_now)
    end = start + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"Event '{summary}' created: {created.get('htmlLink')}"
