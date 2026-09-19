# Module 11 — GCP CLI Commands

Every setup step for this module that can be done from the CLI, exactly as
it was run. This module provisions **no billable infrastructure** (no
databases, VMs or instances) — it only needs APIs enabled, one API key, and
a one-time OAuth consent. That OAuth step is the one thing with no CLI
equivalent; it's documented under "Manual steps" below.

Module 11 has no `.bat` files, so there is no `bat-files/` folder here.

Project used throughout:

```
Project name:   GCP FDE Project
Project ID:     gcp-fde-project
Project number: 1039893753206
```

---

## 0. One-time project setup

```bash
gcloud config set project gcp-fde-project

# Application Default Credentials — used by Vertex AI Gemini (00_setup.py, llm.py)
gcloud auth application-default login
gcloud auth application-default set-quota-project gcp-fde-project

# Maps Platform requires billing enabled on the project
gcloud billing projects describe gcp-fde-project --format="value(billingEnabled)"
```

Python environment (inside `11-tool-calling-integrations/`):

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

---

## Topics 1, 2 — Function calling recap, REST APIs

No GCP setup. Run directly:

```bash
./.venv/bin/python 00_setup.py                 # Vertex AI sanity check -> "setup OK"
./.venv/bin/python 01_function_calling_recap.py
./.venv/bin/python 02_rest_apis.py
```

---

## Topic 3 — Google APIs: enable the APIs

`aiplatform.googleapis.com` (Vertex AI) was already enabled on this project.
These five were not:

```bash
gcloud services enable \
  gmail.googleapis.com \
  calendar-json.googleapis.com \
  geocoding-backend.googleapis.com \
  directions-backend.googleapis.com \
  apikeys.googleapis.com \
  --project=gcp-fde-project
```

Confirm all six are on:

```bash
gcloud services list --enabled --project=gcp-fde-project --format="value(config.name)" \
  | grep -E "^(gmail|calendar-json|geocoding-backend|directions-backend|apikeys|aiplatform)\."
```

Note: `directions-backend.googleapis.com` is Google's *legacy* Directions API.
It is still listed as available and enabled cleanly on this project, and the
`googlemaps` Python library used here calls it.

---

## Topic 6 — Maps API key (created here because topic 3's `.env` needs it)

Create a key restricted to just the two APIs this module calls. The command
returns an operation, so list the keys afterwards to see the new one:

```bash
gcloud services api-keys create \
  --project=gcp-fde-project \
  --display-name="module-11-maps-key" \
  --api-target=service=geocoding-backend.googleapis.com \
  --api-target=service=directions-backend.googleapis.com

gcloud services api-keys list --project=gcp-fde-project \
  --format="table(displayName,name,restrictions.apiTargets[].service.list():label=RESTRICTED_TO)"
```

Result on this run:

```
DISPLAY_NAME        NAME                                                                               RESTRICTED_TO
module-11-maps-key  projects/1039893753206/locations/global/keys/9305be2d-5ac3-4afd-a407-dfcd0ed6729c  geocoding-backend.googleapis.com,directions-backend.googleapis.com
```

Read the key's value straight into `.env` without printing it. The key string
itself is deliberately **not** written in this file: this repo is public, and a
key that bills against the project shouldn't sit in git history even if it is
restricted.

```bash
gcloud services api-keys get-key-string 9305be2d-5ac3-4afd-a407-dfcd0ed6729c \
  --project=gcp-fde-project --location=global --format="value(keyString)"
# paste the output into .env as MAPS_API_KEY=...
```

Run the Maps demo:

```bash
./.venv/bin/python 06_maps_tool.py
```

Output on this run: the geocoded address for 1600 Amphitheatre Parkway,
its lat/lng, and a walking time of `1 hour 26 mins` for Golden Gate Bridge to
Fisherman's Wharf.

---

## Manual steps — no CLI equivalent (do once, in a browser)

Google has no supported `gcloud` command for creating an OAuth consent screen
or a Desktop OAuth client, and the "Allow" click can't be scripted (the module
docs say the same). One account is used for all of it, both to configure the
project and as the Gmail/Calendar account the assistant acts on:
`mentordivesh@gmail.com` (the project Owner). Sign into the browser as that
account for every step below:

1. Open https://console.cloud.google.com/apis/credentials/consent?project=gcp-fde-project
   On this project a consent screen **already existed, named "LUXE"**
   (External, Testing). There is one consent screen per project and every
   OAuth client shows its name, so nothing needed creating. If your project has
   none, create one: app name, support + developer contact email, **External**,
   no scopes (the code requests them).
2. **Audience -> Test users -> Add users**: `mentordivesh@gmail.com`. While an
   External app is in "Testing", only listed test users can consent. Skipping
   this gave `Error 403: access_denied` ("Access blocked ... can only be
   accessed by developer-approved testers") on the first attempt here.
3. Open https://console.cloud.google.com/apis/credentials?project=gcp-fde-project
   -> **Create credentials -> OAuth client ID** -> Application type
   **Desktop app** (not Web application) -> Create -> **Download JSON**.
4. Rename the download to `client_secret.json` and put it in
   `11-tool-calling-integrations/`. It is gitignored; never commit it.

Confirm the file is the right type without printing the secret (a Desktop client
has a top-level `installed` key; a Web client has `web` and won't work here):

```bash
python3 -c "import json; print(list(json.load(open('client_secret.json')).keys()))"
# -> ['installed']
```

Then run the consent flow. macOS opened Safari by default; forcing Chrome:

```bash
BROWSER='open -a "Google Chrome" %s' ./.venv/bin/python 03_google_apis_oauth_setup.py
```

Click through Google's "app isn't verified" warning (expected for a
Testing-mode app), tick the permissions and **Allow**. This creates
`token.json`. Confirm it, again without printing the token:

```bash
python3 -c "import json; t=json.load(open('token.json')); print(t['scopes'], 'refresh_token:', bool(t.get('refresh_token')))"
# -> ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/calendar'] refresh_token: True
```

---

## Topics 4, 5, 7 and the combined agent

```bash
./.venv/bin/python 04_gmail_tool.py
./.venv/bin/python 05_calendar_tool.py
./.venv/bin/python 07_authentication_demo.py
./.venv/bin/python -W ignore main.py
```

Topics 4 and 5 print parts of a real inbox and calendar, so on this run their
output was redirected to a file and only the result lines were read
(`./.venv/bin/python 04_gmail_tool.py > out.txt`).

What each did, and how it was checked independently rather than trusting the
script's own success message:

- **Topic 4 (Gmail):** read 3 messages and sent "Test from Module 11" to
  `mentordivesh@gmail.com`. Verified by searching Gmail for that subject: the
  new message was there with labels `SENT` and `INBOX`. An older message with
  the same subject (2026-08-07, from an earlier run of this demo on that
  account, different recipient) also matched and was left alone.
- **Topic 5 (Calendar):** the calendar was free, so it created "Team Meeting
  (Module 11 demo)". Verified with `events().list(...)`.
- **Topic 7 (Authentication):** printed the three auth patterns working:
  API key geocoded Mumbai, OAuth reported `acting as mentordivesh@gmail.com`,
  and the ADC Vertex AI client was created for `gcp-fde-project`.
- **`main.py` (combined agent):** three questions. The third chained
  `check_availability` -> `create_event` -> `send_email`. Verified afterwards:
  a sent email "Module 11 Demo Meeting Booked" to `mentordivesh@gmail.com` and a
  calendar event "Module 11 Demo Meeting" exactly 3 hours after the run
  (23:18 IST).

The verification used the module's own auth, e.g.:

```bash
./.venv/bin/python - <<'EOF'
from googleapiclient.discovery import build
from personal_assistant.auth import get_credentials
g = build("gmail", "v1", credentials=get_credentials())
print(len(g.users().messages().list(userId="me", q='subject:"Test from Module 11"').execute().get("messages", [])))
EOF
```

### Real bugs found and fixed

- **Agent answers printed as a raw Python list.** With current
  `langchain-google-genai` (4.4.0), Gemini's `message.content` can be a list of
  content blocks carrying an opaque "thought signature", so the third answer
  printed as `[{'type': 'text', 'text': '...', 'extras': {'signature': ...}}]`.
  `personal_assistant/pipeline.py` `ask()` now returns `message.text`, which is
  the plain string for both shapes. Re-tested with read-only questions (no
  duplicate email/event); all returned `str`.
- **`requirements.txt` relied on transitive installs.** `google-genai` and
  `google-auth` are imported directly but weren't listed. Added.
- **Left as is:** `datetime.utcnow()` is deprecated on Python 3.14 and prints a
  `DeprecationWarning` in topic 5 and the calendar tool. It still works.

---

## Cleanup

Nothing here is billable: no databases, VMs or instances were created. The
APIs, the API key and the OAuth client cost nothing to leave in place. These are
the commands for when you want everything removed. **They have not been run.**

```bash
# the Maps key created above
gcloud services api-keys delete 9305be2d-5ac3-4afd-a407-dfcd0ed6729c \
  --project=gcp-fde-project --location=global

# the two calendar events the demo created
./.venv/bin/python - <<'EOF'
from googleapiclient.discovery import build
from personal_assistant.auth import get_credentials
c = build("calendar", "v3", credentials=get_credentials())
for eid in ("104m4v1jol7pnr3injrhkn5m04", "nq495t89nv09pqtsq77i1mcn2k"):
    c.events().delete(calendarId="primary", eventId=eid).execute()
EOF

# local credentials (both are gitignored)
rm token.json client_secret.json

# optional: turn the APIs back off
gcloud services disable gmail.googleapis.com calendar-json.googleapis.com \
  geocoding-backend.googleapis.com directions-backend.googleapis.com \
  apikeys.googleapis.com --project=gcp-fde-project
```

Two things cleanup can't do from here:

- **The two test emails stay in the inbox.** The token only has the
  `gmail.readonly` and `gmail.send` scopes, which can't delete or trash mail.
- **Revoking access and deleting the OAuth client are browser-only:** remove the
  app at https://myaccount.google.com/permissions and delete the client under
  https://console.cloud.google.com/apis/credentials?project=gcp-fde-project
  (leave the "LUXE" consent screen itself alone; it isn't ours).
