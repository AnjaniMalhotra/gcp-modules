"""Calendar as an agent tool — wraps topic 5's freebusy + create-event logic,
plus a read-only list_events so the assistant can answer "what are my plans?"."""

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


@tool
def list_events(start_date: str = "", days: int = 1) -> str:
    """List the user's calendar events (title and start time) for `days` whole
    days beginning on `start_date` (YYYY-MM-DD in the user's local time; empty
    means today). Use this for "what are my plans today / tomorrow / this
    week". Events are listed with start and end, so one that begins the evening
    before and runs past midnight shows up on the next day too. Read-only."""
    service = _get_calendar_service()
    tz = datetime.now().astimezone().tzinfo
    day = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
    start = datetime(day.year, day.month, day.day, tzinfo=tz)
    events = service.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=(start + timedelta(days=days)).isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=50,
    ).execute().get("items", [])

    if not events:
        return f"No events for {days} day(s) starting {start.date()}."
    return "\n".join(
        f"{e['start'].get('dateTime', e['start'].get('date'))} to "
        f"{e['end'].get('dateTime', e['end'].get('date'))} - {e.get('summary', '(no title)')}"
        for e in events
    )
