# Module 11 — Project notes: Personal Assistant Agent

## What it is

A command-line assistant. You type a request in plain English; Gemini (through
Vertex AI, wired up with LangChain) decides which of seven tools to call across
Gmail, Google Calendar and Google Maps, calls them for real, and answers. It acts
on whichever Google account you sign in with.

Three ways to run it, from the module folder:

| Command | What it does |
|---|---|
| `./.venv/bin/python main.py --chat` | A conversation. It remembers earlier turns, so follow-ups work |
| `./.venv/bin/python main.py "What are my plans today?"` | One question, then exit |
| `./.venv/bin/python main.py` | The fixed 3-question demo (books an event and sends an email) |

At start-up it is told the current date, time and timezone, so "tomorrow at 3pm"
works without it asking what time it is.

## What it can do

All seven tools were run for real during this project and checked through the
Gmail and Calendar APIs.

| You can ask | Tool | What it returns or does | Changes anything? |
|---|---|---|---|
| "What are my plans tomorrow?" / "this week?" | `list_events(start_date, days)` | Title, start and end of each event, up to 50 | No |
| "Am I free tomorrow at 3pm?" | `check_availability(hours_from_now, duration_minutes)` | Whether that slot is free, or which times are busy | No |
| "Book a 30 minute meeting in 3 hours" | `create_event(summary, hours_from_now, duration_minutes)` | A new event on your main calendar | **Yes** |
| "Email me that it's booked" | `send_email(to, subject, body)` | Sends a plain-text email | **Yes** |
| "Show my 3 most recent emails" | `read_recent_emails(max_results)` | A short preview (snippet) of each | No |
| "Address of the Taj Mahal" | `get_address_details(place)` | Full address and coordinates | No |
| "How far is Delhi to Agra by car?" | `get_directions(origin, destination, mode)` | Distance and travel time | No |

It can chain them on its own. The demo's third question does availability check,
then create event, then send email, from a single sentence. Directions work for
driving, walking, bicycling or transit; driving and walking were the ones tested.

## What it can't do (yet)

- **Calendar:** see event details beyond title and times (no description, place or
  attendees); edit, move or delete events; invite people; make recurring events;
  use any calendar except your main one.
- **Email:** read a full message (previews only); search; open a thread; reply;
  attach files; delete or label mail. The login only has read and send
  permission, so it can never delete or edit email.
- **Maps:** search for places, ratings or opening hours; step-by-step directions.
- **Memory:** it remembers only within one `--chat` session. Quit and it forgets.
- **Where it runs:** on your machine only. The sign-in needs a browser, so it isn't
  deployed anywhere (deployment starts in Module 14).
- **Multi-agent:** it is one agent with seven tools. Splitting it into a
  Gmail agent, a Calendar agent and a Maps agent is left for the LangGraph module.

## Good to know

- **It really sends and creates.** Anything you ask it to email or book actually
  happens. Check Google Calendar and Gmail (Sent) afterwards.
- **It checks availability first, by instruction, not by rule.** The prompt tells
  it to check the calendar before booking, and it did (a second demo run within 3
  hours correctly refused to double-book). It is still a language model, so for
  anything important, glance at the calendar.
- **What it reads is sent to Gemini.** Event titles and email previews returned by
  a tool are part of the conversation the model sees.
- **The login expires.** Google typically expires the sign-in about every 7 days
  while the app is in Testing mode. If a run fails with `invalid_grant`, delete
  the token file and run `03_google_apis_oauth_setup.py` again.
- **One login file per account.** Set `TOKEN_FILE` (see `commands.md`) to switch
  between Google accounts without overwriting either.
- **The sign-in screen says "LUXE".** The project already had a consent screen with
  that name before this module. It is only a label, and it is not part of this
  module.
- **Cost:** effectively nothing. Gmail and Calendar are free, Maps is inside its
  monthly free credit at this scale, and Gemini usage here is a few small requests.

## Links used

**Google Cloud Console** (project `gcp-fde-project`, signed in as a project owner)

- OAuth consent screen and test users: https://console.cloud.google.com/apis/credentials/consent?project=gcp-fde-project
- Credentials, where the Desktop OAuth client is created and its JSON downloaded: https://console.cloud.google.com/apis/credentials?project=gcp-fde-project
- Revoke this app's access to your Google account at any time: https://myaccount.google.com/permissions

**GitHub**

- Repository: https://github.com/AnjaniMalhotra/gcp-modules
- This module's branch: https://github.com/AnjaniMalhotra/gcp-modules/tree/11-tool-calling-integration

**What the code talks to** (through the Google client libraries unless noted)

- Google sign-in (OAuth): https://accounts.google.com/o/oauth2/auth
- Gmail API: https://gmail.googleapis.com/gmail/v1/
- Calendar API: https://www.googleapis.com/calendar/v3/
- Maps geocoding: https://maps.googleapis.com/maps/api/geocode/json
- Maps directions (Google's legacy Directions API): https://maps.googleapis.com/maps/api/directions/json
- Vertex AI (Gemini): https://aiplatform.googleapis.com
- Permission scopes requested: `https://www.googleapis.com/auth/gmail.readonly`, `.../gmail.send`, `.../calendar`
- Only in the parked lesson demo `deleteds/02_rest_apis.py`: https://uselessfacts.jsph.pl/api/v2/facts/random

## Where to look next

- [`README.md`](README.md): layout, setup, and how to test it
- [`commands.md`](commands.md): every `gcloud` command run, with real values, plus the one browser-only step
- [`docs/`](docs/): the seven lessons
- [`deleteds/README.md`](deleteds/README.md): the lesson demo scripts that are parked, and why
