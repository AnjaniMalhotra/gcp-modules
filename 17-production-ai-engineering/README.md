# Code — Module 17: Production AI Engineering

One small, self-contained Flask service, **ModeraAI** (a content moderation API), hardened topic by topic against real production failure modes: bursty traffic, unreliable dependencies, hangs, abuse, and cost blowups. It uses no code from any other module.

**Scope note:** the service is deployed `--allow-unauthenticated`, so anyone with its URL can call it (and cause Gemini calls). That keeps every topic testable with a plain `curl`, but delete the service when you finish.

## Layout

```
17-production-ai-engineering/
├── moderaai/                  the service: main.py, Dockerfile, requirements.txt, cloudbuild.yaml
│                              (keep this path: the CI/CD trigger and cloudbuild.yaml point at it)
├── scripts/
│   ├── load_test.py           fires N concurrent requests (topics 1 and 9)
│   └── cost_comparison_demo.py  Flash vs Pro tokens, and what caching saves (topic 10)
├── gateway/
│   └── openapi_spec.yaml      the API Gateway definition with the 10-requests-a-minute quota
├── docs/                      the lessons: one file per topic
├── bat-files/                 the original Windows .bat scripts, kept for reference
├── commands.md                every gcloud command run, with real values, and what each showed
├── PROJECT_NOTES.md           what was found, what it can't do, where to look in the Console
├── requirements.txt           for the two scripts
└── .env.example
```

The scripts and the gateway spec were moved into `scripts/` and `gateway/` after the run, to tidy the folder. The
`.bat` files in `bat-files/` are the unchanged originals, so they still use the old locations.

## The ten topics

| # | Topic | What you do | Run with |
|---|---|---|---|
| 1 | Scaling | 50 concurrent requests, count the instances, then cap them | `scripts/load_test.py` |
| 2 | Cloud Build | build, push and deploy with one remote command | `gcloud builds submit` |
| 3 | CI/CD | a push to GitHub deploys the service by itself | a Cloud Build trigger |
| 4 | Versioning | deploy v2 next to v1 at 0% traffic | `gcloud run deploy --no-traffic --tag` |
| 5 | Rollbacks | promote v2, see it wrongly flag safe text, roll back to v1 | `gcloud run services update-traffic` |
| 6 | Caching | the same text twice: the second answer is instant | built into `main.py` |
| 7 | Retries | `?simulate_transient_failure=true` fails twice, then succeeds | built into `main.py` |
| 8 | Timeouts | `?simulate_hang=true` stalls and gets cut off | built into `main.py` |
| 9 | Rate limiting | API Gateway limits each project to 10 requests a minute | `gateway/openapi_spec.yaml` |
| 10 | Cost | Flash against Pro, and how many Gemini calls caching avoids | `scripts/cost_comparison_demo.py` |

## Setup

All the infrastructure is created with `gcloud`: see [`commands.md`](commands.md). The `.bat` scripts in `bat-files/` are the Windows-only originals of the same steps.

```bash
cp .env.example .env
# ...set PROJECT_ID and GITHUB_USERNAME
sed -i '' 's/\r$//' .env .env.example requirements.txt moderaai/requirements.txt   # only if they have Windows line endings
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
gcloud auth application-default login
set -a && source .env && set +a
```

**Line endings matter.** The course files use Windows (CRLF) line endings, which break `source .env` on macOS and Linux and leave a hidden character on every value. `commands.md` has the details. The `.bat` files must keep their CRLF.

## Run order

Follow [`commands.md`](commands.md); the order matters:

1. Setup: the Artifact Registry repo, the Firestore database, the `moderaai-sa` service account and its two roles.
2. Topic 1: deploy v1, copy the printed Service URL into `.env` as `SERVICE_URL`, then load-test.
3. Topic 2: the manual Cloud Build, run from the **repo root**.
4. Topic 3: needs your GitHub account: a one-time browser authorisation, then the trigger and a real push.
5. Topics 4 and 5: v2 and the rollback. The service's *settings* stay at whatever the last deploy set, so deploy with `MODERATION_POLICY` set explicitly afterwards.
6. Topics 6 to 8: `curl` calls against the service.
7. Topic 9: put the real service URL in `gateway/openapi_spec.yaml`, create the gateway (about 11 minutes), then the API key, which is restricted to this API.
8. Topic 10: `./.venv/bin/python scripts/cost_comparison_demo.py`.
9. Teardown, at the end of `commands.md`.

## What was changed from the course files

The service and scripts were corrected where running them for real showed a problem: the cache key ignored the moderation policy (which made the rollback demo look like it did nothing), `/healthz` is reserved by Cloud Run, retries were never logged, the build paths assumed a different repo layout, and a few scripts had wrong flags. The full list, with what each one looked like when it went wrong, is in [`PROJECT_NOTES.md`](PROJECT_NOTES.md).

## Cost note

Cloud Run, Cloud Build, Artifact Registry, Firestore and API Gateway all stay inside their free tiers for this module's load. The only real spend is the Gemini calls, kept small by the module's own caching. Nothing here bills by the hour the way Redis and Cloud SQL do, but the public service is still worth deleting when you finish.
