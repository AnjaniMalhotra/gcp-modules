# Teacher Plan — Module 11: Tool Calling & Integrations

**Total time:** 3 hrs (180 min) — includes a 10 min buffer.
**Format this module:** Python throughout, one file per concept, building toward one combined agent by the end.

## Before you start recording/teaching

- [ ] Complete the OAuth Console setup from topic 3's doc **before recording** — consent screen, OAuth Client ID, `client_secret.json` downloaded
- [ ] Run `03_google_apis_oauth_setup.py` once yourself, click through the browser consent screen, confirm `token.json` gets created
- [ ] Get a Maps Platform API key (topic 6) — restrict it to Geocoding + Directions APIs only, least privilege
- [ ] `gcloud services enable gmail.googleapis.com calendar-json.googleapis.com` already run on your project
- [ ] Have a real (test) email address ready to send a demo email to — don't spam a real contact

## Suggested pacing (180 min)

| # | Topic | Minutes | Format |
|---|-------|---------|--------|
| 1 | Function Calling | 15 | Fast recap |
| 2 | REST APIs | 20 | Talk + generic API demo |
| 3 | Google APIs | 25 | OAuth Console walkthrough + quickstart |
| 4 | Gmail API | 30 | Talk + send/read demo |
| 5 | Calendar API | 30 | Talk + availability/create demo |
| 6 | Maps API | 20 | Quick demo, API key contrast |
| 7 | Authentication | 30 | Deep-dive comparison + combined agent demo |
| — | Buffer | 10 | — |

## Teaching order rationale

Keep the syllabus order. Topics 1-2 are foundation (you already know function calling; REST APIs is the general shape every integration follows). Topic 3 is the unlock — get OAuth working once, and topics 4-5 just consume it. Topic 6 is a deliberate contrast (API key, no OAuth needed) to make topic 7's comparison land harder. Topic 7 closes both with the formal auth theory AND the combined Personal Assistant Agent demo.

## Per-Component Focus

### 1. Function Calling
**Land this one idea:** "You've done this twice already (Module 3, Module 10) — this module is about pointing that same mechanism at the real world."
- Keep this fast — a recap, not a re-teach. If you're spending more than 15 minutes here, you're re-teaching.

### 2. REST APIs
**Land this one idea:** "Every API integration is the same shape: build a request, send it, parse the response, hand it back to the model." 
- Demo: call a simple public REST API (no auth needed) directly with `requests`, wrap it as a LangChain tool.
- Common confusion: students conflate "REST API" with "Google API" — clarify REST is the general pattern; Google APIs (topic 3) are a specific, convenience-wrapped case of it.

### 3. Google APIs
**Land this one idea:** "Gmail and Calendar act AS YOU — that needs your explicit, one-time, in-browser permission. This is different from every auth pattern used so far in this course."
- This topic carries the heaviest non-coding load in the module — the OAuth Console walkthrough. Do this screen-recording-style, slowly, since it's the one part students must replicate themselves.
- Demo: run `03_google_apis_oauth_setup.py` live, click "Allow" in the browser, show `token.json` appear.
- Common confusion: students think this needs a service account like every earlier module. Explicitly contrast: service accounts act as themselves; OAuth here acts as a specific human user.

### 4. Gmail API
**Land this one idea:** "Same OAuth token from topic 3 unlocks this — no new auth setup needed."
- Demo: read the 3 most recent emails, then send one (to a test address you control).
- Common confusion: forgetting Gmail messages must be base64url-encoded MIME, not plain text — show the encoding step explicitly, don't hide it.

### 5. Calendar API
**Land this one idea:** "Two operations matter most for an assistant: check free/busy, then create an event."
- Demo: query freebusy for today, then create a test event, then show it actually appears in the real Calendar UI (a good "it's real" moment).
- Common confusion: time zone handling — always show an explicit RFC3339 timestamp with timezone, never a naive datetime.

### 6. Maps API
**Land this one idea:** "This one just needs an API key — no OAuth dance, because it's not touching anyone's private data."
- Demo: geocode an address, then get directions between two points.
- Common confusion: assuming ALL Google APIs need OAuth. Explicitly use this topic to break that assumption before topic 7 formalizes the comparison.

### 7. Authentication
**Land this one idea:** "Three different auth patterns, three different reasons — API key (public data), OAuth (acting as a user), service account (acting as itself). Picking the right one is a security decision, not a formality."
- Demo: `07_authentication_demo.py` runs all three patterns side by side against their respective APIs, printing which credential type was used for each.
- Close the module with the combined **Personal Assistant Agent** demo — the "check Thursday, schedule it, email directions" request from the module overview, run live.
- Common confusion: students think "more permissions = safer to just always use." Reinforce least-privilege scoping explicitly (e.g., `gmail.send` instead of full Gmail access) — ties back to Module 2's IAM lesson.

## Wrap-up

- Run the combined agent live, one more time, with a question the student comes up with on the spot
- Rapid-fire recap: one question from each topic's "Quick Recap" (7 questions)
- Explicit reminder: multi-agent versions of this exact assistant come later, in the LangGraph module — not here
