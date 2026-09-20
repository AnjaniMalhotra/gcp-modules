# Module 17 — GCP CLI Commands

Every step for this module, done with `gcloud` (and `curl`) only, exactly as it was run on
2026-09-20. These replace the Windows-only `.bat` scripts, which are kept unchanged in
[`bat-files/`](bat-files/) for reference. Nothing in this module needs a password; the only
secret is the API key created in topic 9, which stays in the gitignored `.env`.

> **Paths.** The run used the files where the course put them (at the module root). They were moved afterwards to
> `scripts/load_test.py`, `scripts/cost_comparison_demo.py` and `gateway/openapi_spec.yaml`; the commands below use the
> new paths, and everything else is exactly as it was run.

```
Project name:   GCP FDE Project
Project ID:     gcp-fde-project
Project number: 1039893753206
Region:         us-central1
Service URL:    https://moderaai-1039893753206.us-central1.run.app
```

---

## 0. Setup

All the APIs this module needs (Cloud Run, Cloud Build, Artifact Registry, Firestore, Vertex AI,
API Gateway, Service Management, Service Control, API Keys) were already enabled on the project.
Confirm:

```bash
gcloud services list --enabled --project=gcp-fde-project --format="value(config.name)" \
  | grep -E "^(run|cloudbuild|artifactregistry|firestore|aiplatform|apigateway|servicemanagement|servicecontrol|apikeys)\."
```

Create `.env` (Unix line endings; the course files are Windows CRLF, which breaks `source .env`):

```bash
cd 17-production-ai-engineering
cp .env.example .env
sed -i '' 's/\r$//' .env .env.example requirements.txt moderaai/requirements.txt
sed -i '' -e 's|^PROJECT_ID=.*|PROJECT_ID=gcp-fde-project|' -e 's|^GITHUB_USERNAME=.*|GITHUB_USERNAME=AnjaniMalhotra|' .env
set -a && source .env && set +a
```

One-time resources (what `00a_initial_setup.bat` does):

```bash
gcloud artifacts repositories create moderaai-repo --project=gcp-fde-project \
  --repository-format=docker --location=us-central1 --description="Container images for ModeraAI (Module 17)"

gcloud firestore databases create --project=gcp-fde-project --location=us-central1 --type=firestore-native

gcloud iam service-accounts create moderaai-sa --project=gcp-fde-project --display-name="ModeraAI Runtime SA"

# least privilege: call Gemini, and read/write Firestore
gcloud projects add-iam-policy-binding gcp-fde-project \
  --member="serviceAccount:moderaai-sa@gcp-fde-project.iam.gserviceaccount.com" --role="roles/aiplatform.user" --condition=None
gcloud projects add-iam-policy-binding gcp-fde-project \
  --member="serviceAccount:moderaai-sa@gcp-fde-project.iam.gserviceaccount.com" --role="roles/datastore.user" --condition=None
```

Python environment for the local test scripts (`scripts/load_test.py`, `scripts/cost_comparison_demo.py`):

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
```

---

## Topic 1 — Scaling

Deploy v1 (`01_deploy_and_load_test.bat`). Took about 3 minutes, including the image build:

```bash
gcloud run deploy moderaai --source moderaai --project=gcp-fde-project --region=us-central1 \
  --allow-unauthenticated \
  --service-account=moderaai-sa@gcp-fde-project.iam.gserviceaccount.com \
  --set-env-vars=PROJECT_ID=gcp-fde-project,LOCATION=us-central1,MODERATION_POLICY=standard,MODEL_NAME=gemini-2.5-flash,GEMINI_TIMEOUT_MS=10000,CACHE_TTL_SECONDS=3600 \
  --max-instances=10 --timeout=30 --quiet
# -> Service URL: https://moderaai-1039893753206.us-central1.run.app   (revision moderaai-00001-gjh)
```

Google also created a second Artifact Registry repo, `cloud-run-source-deploy`, for the source build.
It is removed in the teardown.

Save the URL in `.env`, then call it:

```bash
sed -i '' 's|^SERVICE_URL=.*|SERVICE_URL=https://moderaai-1039893753206.us-central1.run.app|' .env
curl -X POST $SERVICE_URL/moderate -H "Content-Type: application/json" -d '{"text": "I hate you, you are so stupid and ugly"}'
# -> {"category":"harassment","flagged":true,"policy":"standard", ...}
```

### Gotcha 1: `/healthz` is not reachable on Cloud Run

`curl $SERVICE_URL/healthz` returned **Google's own 404 page**, not Flask's: Cloud Run reserves that path
on its public `run.app` URLs. The route was renamed `/health` in `moderaai/main.py` (and in
`gateway/openapi_spec.yaml`).

### Gotcha 2: 50 requests do not scale it up as shipped

The first load test (`python scripts/load_test.py --url $SERVICE_URL --requests 50`) succeeded 50/50, but **all 50 were
served by one instance**: Cloud Run's default is 80 concurrent requests per instance. To make scaling visible,
concurrency was lowered:

```bash
gcloud run services update moderaai --project=gcp-fde-project --region=us-central1 --concurrency=5 --quiet
```

The instance count is read from the request logs (the Console graph lags by minutes):

```bash
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=moderaai AND httpRequest.requestMethod=POST AND timestamp>="<START>"' \
  --project=gcp-fde-project --limit=200 --format="value(labels.instanceId)" | sort | uniq -c
```

| Run | max-instances | concurrency | Instances that served the 50 requests | Wall time |
|---|---|---|---|---|
| 1 | 10 | 80 (default) | **1** | 8.6 s |
| 2 | 10 | 5 | **10** (5–7 requests each) | 10.8 s |
| 3 | 2 | 5 | **2** | 9.8 s |

The ceiling is proved by the instance count (10, then 2). The wall time barely changed, because the Gemini call
dominates and extra requests just queue. Put the ceiling back afterwards:

```bash
gcloud run services update moderaai --project=gcp-fde-project --region=us-central1 --max-instances=10 --quiet
```

### Caching, seen early (topic 6 is built into the service)

The same text twice: 2.2 s the first time (real Gemini call), 0.45 s the second (`"cache_hit": true`).
`gcloud firestore` has no "read documents" command, so the cache was read with the client library:

```bash
./.venv/bin/python -c "
from google.cloud import firestore
for d in firestore.Client(project='gcp-fde-project').collection('moderation_cache').stream():
    print(d.id[:12], d.to_dict()['flagged'], d.to_dict()['category'])"
```

### Gotcha 3: the cache ignored the moderation policy (a bug in the course code)

The cache key was only the text. In topic 5 a verdict cached under v2 (strict) would be served after rolling
back to v1 (standard), so the rollback would look like it changed nothing. The policy is now part of the key
(`content_hash` in `moderaai/main.py`).

---

## Topic 2 — Cloud Build (manual build, push and deploy)

`moderaai/cloudbuild.yaml` was written for the course's repo layout (`code/17-production-ai-engineering/…`).
Its `dir:` line was changed to this repo's layout (`17-production-ai-engineering/moderaai`), and the build is
submitted from the **repo root**, because that is what the topic 3 trigger will also check out.

Before uploading the whole repo as build source, check exactly which files would go (`.env` and tokens are
excluded by `.gitignore`):

```bash
cd ..                                       # repo root
gcloud meta list-files-for-upload .         # 34 files on this run, none secret-looking
```

Build, push and deploy in one command (`02_cloud_build_manual.bat`). Took 2 min 17 s:

```bash
gcloud builds submit --project=gcp-fde-project \
  --config=17-production-ai-engineering/moderaai/cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_TAG=v1.0.0 .
# -> revision moderaai-00005-zx7 deployed, 100% of traffic
```

The build has three steps: `docker build`, `docker push` to Artifact Registry, and `gcloud run deploy`.
The deploy step printed one warning, `Setting IAM policy failed`: the build's service account may not change who
can call the service. It is harmless here, because the service was already public from topic 1 (checked below).

Verify what the build left behind:

```bash
gcloud builds list --project=gcp-fde-project --limit=3
gcloud artifacts docker images list us-central1-docker.pkg.dev/gcp-fde-project/moderaai-repo --include-tags
# -> moderaai   v1.0.0
gcloud run services describe moderaai --region=us-central1 --project=gcp-fde-project   # concurrency 5, max 10, moderaai-sa, 6 env vars kept
gcloud run services get-iam-policy moderaai --region=us-central1 --project=gcp-fde-project   # allUsers still has run.invoker
curl $SERVICE_URL/health      # -> {"policy":"standard","status":"ok"}
```

The deploy step in `cloudbuild.yaml` passes no environment variables or service account. That works only because
the service already existed from topic 1 and `gcloud run deploy` keeps the existing settings.

The cache fix from topic 1 was confirmed on this new revision: the same text with different capitalisation and
spaces came back with `cache_hit: true`.

---

## Topic 3 — CI/CD (push to GitHub, it deploys itself)

`03_create_ci_cd_trigger.bat` uses the older ("1st generation") GitHub connection, which can only be made by
clicking through the Console. This run used the newer connection instead: everything is a command except one
browser authorisation.

**1. Secret Manager, which the connection needs.** The first attempt failed with
`could not assert Secret Manager permissions`. Cloud Build stores GitHub's token in Secret Manager, so its own
service agent needs the API and the role:

```bash
gcloud services enable secretmanager.googleapis.com --project=gcp-fde-project
gcloud projects add-iam-policy-binding gcp-fde-project \
  --member="serviceAccount:service-1039893753206@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin" --condition=None
```

**2. Create the connection.** It stays `PENDING_USER_OAUTH` and prints a link. Open the link in a browser signed in
to the Google account that owns the project, authorise GitHub as the repo owner, and install the Cloud Build
GitHub App on the repository. This is the one step that cannot be a command.

```bash
gcloud builds connections create github moderaai-github --region=us-central1 --project=gcp-fde-project
gcloud builds connections describe moderaai-github --region=us-central1 --project=gcp-fde-project   # installationState: COMPLETE
```

**3. Link the repo and create the trigger.** It watches only the module's branch, and only changes under
`moderaai/`, so other commits do not redeploy anything. It runs as the same service account the manual build
in topic 2 used:

```bash
gcloud builds repositories create gcp-modules --remote-uri=https://github.com/AnjaniMalhotra/gcp-modules.git \
  --connection=moderaai-github --region=us-central1 --project=gcp-fde-project

gcloud builds triggers create github --name=moderaai-deploy-trigger --region=us-central1 --project=gcp-fde-project \
  --repository=projects/gcp-fde-project/locations/us-central1/connections/moderaai-github/repositories/gcp-modules \
  --branch-pattern='^17-production-ai-engineering$' \
  --build-config=17-production-ai-engineering/moderaai/cloudbuild.yaml \
  --included-files='17-production-ai-engineering/moderaai/**' \
  --service-account=projects/gcp-fde-project/serviceAccounts/1039893753206-compute@developer.gserviceaccount.com
```

**4. Test it with a real push.** `/health` was changed to also report `"service": "moderaai"`, then:

```bash
git push -u origin 17-production-ai-engineering
gcloud builds list --region=us-central1 --project=gcp-fde-project --limit=1
```

### Gotcha: the first triggered build failed instantly

The trigger fired within seconds (the detection works), but the build was rejected before any step ran:

```
invalid argument: if 'build.service_account' is specified, the build must either (a) specify
'build.logs_bucket', ... or (c) use either CLOUD_LOGGING_ONLY / NONE logging options
```

A build that runs as a specific service account has to say where its logs go. Two lines at the end of
`moderaai/cloudbuild.yaml` fixed it, and pushing that fix retriggered the build:

```yaml
options:
  logging: CLOUD_LOGGING_ONLY
```

(The manual build in topic 2 did not need this: it ran with the default legacy log settings.)

### Result

Build `c5d99104-…` ran automatically for commit `0ea7e47` (the same commit as local HEAD), took about 2.5
minutes, and succeeded. Nothing was run by hand. The live service afterwards:

```bash
curl $SERVICE_URL/health      # -> {"policy":"standard","service":"moderaai","status":"ok"}
gcloud run revisions list --service=moderaai --region=us-central1 --project=gcp-fde-project
# -> moderaai-00006-749 active, 100% of traffic   (created by the trigger; this is "v1" from here on)
```

---

## Topic 4 — Versioning (v2 next to v1, at 0% of traffic)

Build and tag the v2 image (37 s), then deploy it as a new revision that receives **no traffic** and has its own
direct URL (`04_deploy_v2_no_traffic.bat`):

```bash
gcloud builds submit moderaai --project=gcp-fde-project \
  --tag=us-central1-docker.pkg.dev/gcp-fde-project/moderaai-repo/moderaai:v2.0.0

gcloud run deploy moderaai --project=gcp-fde-project --region=us-central1 \
  --image=us-central1-docker.pkg.dev/gcp-fde-project/moderaai-repo/moderaai:v2.0.0 \
  --service-account=moderaai-sa@gcp-fde-project.iam.gserviceaccount.com \
  --set-env-vars=PROJECT_ID=gcp-fde-project,LOCATION=us-central1,MODERATION_POLICY=strict,MODEL_NAME=gemini-2.5-flash,GEMINI_TIMEOUT_MS=10000,CACHE_TTL_SECONDS=3600 \
  --no-traffic --tag=v2-0-0 --quiet
# -> moderaai-00007-vuw deployed, 0 percent of traffic
# -> reachable directly at https://v2-0-0---moderaai-mewtpyvzkq-uc.a.run.app
```

Note that "v2" is the same code with `MODERATION_POLICY=strict`: the difference is a setting, not new logic.

### Gotcha: the tag must be at least 3 characters

The script's `--tag=v2` fails with `service.spec.traffic[1].tag: must be at least 3 characters long`. Nothing is
created by the failed attempt. `v2-0-0` works.

Two versions live side by side. The same comment sent to each:

```bash
curl -X POST $SERVICE_URL/moderate -H "Content-Type: application/json" -d '{"text": "I disagree with this policy."}'
# v1 (main URL)   -> flagged: false, policy: standard
# v2 (tagged URL) -> flagged: true,  category: critical, policy: strict
```

Both were cache misses. With the original cache key (text only), v2 would have been handed v1's cached answer
and the difference would have been hidden.

---

## Topic 5 — Rollbacks

```bash
# 1. ship v2 to everyone
gcloud run services update-traffic moderaai --region=us-central1 --project=gcp-fde-project --to-latest
# -> moderaai-00007-vuw 100%

# 2. the same mild comment is now wrongly flagged
curl -X POST $SERVICE_URL/moderate -H "Content-Type: application/json" -d '{"text": "I disagree with this policy."}'
# -> flagged: true, policy: strict

# 3. roll back: one command, no rebuild (9 seconds, 16:15:15 to 16:15:24)
gcloud run services update-traffic moderaai --region=us-central1 --project=gcp-fde-project \
  --to-revisions=moderaai-00006-749=100
# -> moderaai-00006-749 100%

# 4. the same comment after the rollback
# -> flagged: false, policy: standard
```

Steps 2 and 4 were both `cache_hit: true`, and each returned the verdict of its own policy. That is the cache-key
fix at work: with the original key, step 4 would have returned v2's cached `flagged: true` for up to an hour and
the rollback would have looked like it had not worked.

Find the revision to roll back to with `gcloud run revisions list --service=moderaai --region=us-central1
--project=gcp-fde-project`. Here the v1 revision (`moderaai-00006-749`) is the one the CI/CD trigger built in
topic 3.

---

## Topic 6 — Caching

Built into `moderaai/main.py`: the answer to each (policy, text) is stored in Firestore for an hour. The same text three
times (`06_test_caching_retries_timeouts.bat`):

```bash
curl -w "\nTime: %{time_total}s\n" -X POST $SERVICE_URL/moderate -H "Content-Type: application/json" \
  -d '{"text": "Nice write-up, I learned a lot from it"}'
# call 1: cache_hit false, 2.92 s   (a real Gemini call)
# call 2: cache_hit true,  0.46 s
# call 3: cache_hit true,  0.46 s
```

The key is a hash of the policy plus the lower-cased, trimmed text, so `"  GREAT ARTICLE  "` and
`"great article"` share an entry (checked in topic 2). Note that the very first call in a session can already be a
hit if the text was sent before (an earlier test call did exactly that).

---

## Topic 7 — Retry strategies

`?simulate_transient_failure=true` makes the call fail twice with a `ConnectionError`, then succeed. The service
retries with `tenacity` (3 attempts, waiting 1 s then 2 s):

```bash
curl -X POST "$SERVICE_URL/moderate?simulate_transient_failure=true" -H "Content-Type: application/json" \
  -d '{"text": "retry demo text"}'
# -> 200, and it took 6.35 s, against 2.36 s for a normal request: about 3 s of waiting between the attempts
```

### Gotcha: the script says to read the retries in the logs, but nothing logged them

`main.py` had no logging on retries, so there was nothing to find. One line was added to the `@retry` decorator
(`before_sleep=before_sleep_log(logger, logging.WARNING)`, plus `logging.basicConfig`). Now:

```bash
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=moderaai AND textPayload:"Retrying"' \
  --project=gcp-fde-project --limit=10 --order=asc --format="value(timestamp,textPayload)"
# 10:50:04 WARNING:moderaai:Retrying main.call_gemini in 1 seconds as it raised ConnectionError: Simulated transient failure (attempt 1).
# 10:50:05 WARNING:moderaai:Retrying main.call_gemini in 2 seconds as it raised ConnectionError: Simulated transient failure (attempt 2).
```

### Gotcha: a rollback moves traffic, not settings

After topics 4 and 5 the service was serving v1 again, but its *settings* (the template new deploys start from) were
still `MODERATION_POLICY=strict`. A plain `gcloud run deploy` with no `--set-env-vars`, and the CI/CD trigger in
topic 3, would have quietly shipped the strict policy. The new code was therefore deployed with the policy set
explicitly, and traffic then pointed at the latest revision again:

```bash
gcloud run deploy moderaai --source moderaai --project=gcp-fde-project --region=us-central1 --allow-unauthenticated \
  --service-account=moderaai-sa@gcp-fde-project.iam.gserviceaccount.com \
  --set-env-vars=PROJECT_ID=gcp-fde-project,LOCATION=us-central1,MODERATION_POLICY=standard,MODEL_NAME=gemini-2.5-flash,GEMINI_TIMEOUT_MS=10000,CACHE_TTL_SECONDS=3600 --quiet
gcloud run services update-traffic moderaai --region=us-central1 --project=gcp-fde-project --to-latest
```

---

## Topic 8 — Timeouts

`?simulate_hang=true` makes the handler sleep 60 seconds:

```bash
curl -w "\nHTTP %{http_code} after %{time_total}s\n" -X POST "$SERVICE_URL/moderate?simulate_hang=true" \
  -H "Content-Type: application/json" -d '{"text": "timeout demo text"}'
# -> HTTP 504 after 30.4 s, body "upstream request timeout"
```

The gcloud log shows what did the cutting: `The request has been terminated because it has reached the maximum
request timeout`. That is **Cloud Run's request timeout (`--timeout=30`), not the app's own 10-second
`GEMINI_TIMEOUT_MS`**, which this switch never reaches: it sleeps before Gemini is called.

To test the app-level timeout for real, a temporary revision was deployed with the Gemini timeout at 1 ms, at 0%
of traffic and with its own URL, called, and then the settings and traffic were put back:

```bash
gcloud run services update moderaai --region=us-central1 --project=gcp-fde-project \
  --update-env-vars=GEMINI_TIMEOUT_MS=1 --no-traffic --tag=timeout-test --quiet
curl -X POST https://timeout-test---moderaai-mewtpyvzkq-uc.a.run.app/moderate -H "Content-Type: application/json" \
  -d '{"text": "gemini timeout test"}'
# -> {"error": "moderation failed", "detail": "RetryError[... raised ConnectTimeout>]"}   (HTTP 502, 14 s including a cold start)

# restore, so the test does not leak into later deploys
gcloud run services update moderaai --region=us-central1 --project=gcp-fde-project \
  --update-env-vars=GEMINI_TIMEOUT_MS=10000 --no-traffic --quiet
gcloud run services update-traffic moderaai --region=us-central1 --project=gcp-fde-project --to-latest --remove-tags=timeout-test
```

So there are two safety nets: the app times the Gemini call out and returns a clean 502 after its retries, and
Cloud Run cuts anything that runs past 30 seconds with a 504.

---

## Topic 9 — Rate limiting with API Gateway (partly proven)

**Result in one line:** the gateway, the API key and the 10-requests-a-minute limit are all set up and working as
configured, and the requests are counted, but **no request was ever rejected with a 429**. Not proven end to end.

Point the OpenAPI spec at the live service (the placeholder `MODERAAI_SERVICE_URL_HERE` is replaced with
`https://moderaai-1039893753206.us-central1.run.app`), then (`09_api_gateway_rate_limit_setup.bat`):

```bash
gcloud api-gateway apis create moderaai-api --project=gcp-fde-project

gcloud api-gateway api-configs create moderaai-config --api=moderaai-api --openapi-spec=gateway/openapi_spec.yaml \
  --backend-auth-service-account=moderaai-sa@gcp-fde-project.iam.gserviceaccount.com --project=gcp-fde-project
```

### Gotcha: a step the course script leaves out

The API has its own Google-managed service, which must be enabled on the project before its key and quota work:

```bash
gcloud api-gateway apis describe moderaai-api --project=gcp-fde-project --format="value(managedService)"
# -> moderaai-api-1s49kcx22x0o6.apigateway.gcp-fde-project.cloud.goog
gcloud services enable moderaai-api-1s49kcx22x0o6.apigateway.gcp-fde-project.cloud.goog --project=gcp-fde-project
```

Create the gateway. This took **10 min 41 s** (16:34:43 to 16:45:24), the slowest step of the module:

```bash
gcloud api-gateway gateways create moderaai-gateway --api=moderaai-api --api-config=moderaai-config \
  --location=us-central1 --project=gcp-fde-project
gcloud api-gateway gateways describe moderaai-gateway --location=us-central1 --project=gcp-fde-project \
  --format="value(state,defaultHostname)"
# -> ACTIVE   moderaai-gateway-d9pxw392.uc.gateway.dev
```

Create the API key. The script's key is unrestricted; this one works **only with this API**. The key string is read
straight into the gitignored `.env` and never printed:

```bash
KEY=$(gcloud services api-keys create --project=gcp-fde-project --display-name="ModeraAI API Key" \
  --api-target=service=moderaai-api-1s49kcx22x0o6.apigateway.gcp-fde-project.cloud.goog \
  --format="value(response.keyString)")
sed -i '' "s|^API_KEY=.*|API_KEY=$KEY|" .env && unset KEY
```

Careful when reading the gateway's logs: the `jsonPayload.api_key` field contains the raw key. Leave it out of any
`--format`.

### What was checked, and what it showed

| Check | Result |
|---|---|
| `POST /moderate` with no key | **401**, "Method doesn't allow unregistered callers" |
| `GET /health` through the gateway | 200 (the spec puts no key on it) |
| `POST /moderate?key=...` | 200 |
| Limit registered in the API's service config | yes: `moderate-limit`, `1/min/{project}`, value 10, cost 1 per request |
| 15 requests in a burst, then 40 in a burst, with the key | **15/15 and 40/40 returned 200, none 429** |
| Requests counted against the quota | yes: Cloud Monitoring `quota/rate/net_usage` showed 15 in one minute, `quota/limit` showed 10 |

Read the config and the counters (the second is a REST call because `gcloud` has no command for it):

```bash
gcloud endpoints configs describe moderaai-config-36830eg9l1o5e \
  --service=moderaai-api-1s49kcx22x0o6.apigateway.gcp-fde-project.cloud.goog --format="yaml(quota)"

curl -G "https://monitoring.googleapis.com/v3/projects/gcp-fde-project/timeSeries" -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  --data-urlencode 'filter=metric.type="serviceruntime.googleapis.com/quota/rate/net_usage" AND resource.labels.service="moderaai-api-1s49kcx22x0o6.apigateway.gcp-fde-project.cloud.goog"' \
  --data-urlencode "interval.startTime=<START>" --data-urlencode "interval.endTime=<END>"
```

The gateway's own log for each call showed `api_key_state: VERIFIED` and `response_code_details: via_upstream`:
the key is recognised and the call is forwarded, but the limit is not applied.

### Why it probably did not block, and what would prove it

The API's project (the "producer") and the project the key belongs to (the "consumer") are the same one,
`gcp-fde-project`. Endpoints quotas are documented as limiting each *consumer* project, so the likely explanation is
that a project's own calls to its own API are not held to the limit. **This is a hypothesis: Google's
documentation pages read for this run did not confirm or deny it.** Proving it needs a key from a second project
acting as a separate customer; that was not done.

One earlier test run of 15 requests is also on record and should be ignored: it took 952 s and showed 9 timeouts
because the laptop stalled mid-run, so it says nothing about the limit.

The topic's other point stands: a rate limit belongs at the front door, declared in the OpenAPI spec, with no
hand-written code in the service.

---

## Topic 10 — Cost optimization

`scripts/cost_comparison_demo.py` needs `PROJECT_ID` (and `SERVICE_URL`) from `.env`, and the ADC login:

```bash
set -a && source .env && set +a
./.venv/bin/python scripts/cost_comparison_demo.py
```

**Part 1: Flash against Pro, same prompt.** The script prints token counts and an estimated cost:

| Model | input | "output" (as printed) | total | estimated cost (script's prices) |
|---|---|---|---|---|
| gemini-2.5-flash | 26 | 115 | 919 | $0.000092 |
| gemini-2.5-pro | 26 | 80 | 1015 | $0.002537 |

The prices in the script are hard-coded illustrative numbers ($0.0001 and $0.0025 per 1K tokens, blended). They were
not checked against Google's current price list, so read the ratio (about 25 times), not the dollars.

**Part 2: what caching really saves, from a request counter.** 6 incoming requests (3 of them duplicates) produced
**3 real Gemini calls, so 3 were avoided**. Checked a second way: the 3 texts were then found in Firestore under the
standard-policy key. The counter (`/stats`) lives in each instance's memory and resets on a cold start, so the
before/after difference is only reliable when one instance answers the whole run, as it did here.

### Finding: most of the tokens are hidden "thinking"

The script's "output tokens" hides them. Gemini 2.5 spends most of its tokens thinking before it answers, and they are
billed as output. For one request (`usage_metadata`):

| Model | prompt | answer | **thinking** | total |
|---|---|---|---|---|
| gemini-2.5-flash | 26 | 183 | **877** | 1086 |
| gemini-2.5-pro | 26 | 119 | **1010** | 1155 |

A moderation verdict is a simple task, so thinking can be switched off. The same request with structured output (as the
service sends it), Flash only, one sample:

```python
config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema,
                                     thinking_config=types.ThinkingConfig(thinking_budget=0))
# thinking on (default):  answer 68, thinking 301, total 414  -> flagged=False
# thinking off (budget 0): answer 37, thinking   0, total  82  -> flagged=False   (about 80% fewer tokens)
```

That is one input, not a quality test. It shows the size of the lever; before using it in the service, compare the
verdicts on a batch of real comments. It was **not applied** to `moderaai/main.py`.

The three cost levers seen in this module, in order of effect: caching (calls avoided entirely), the model choice (Flash
against Pro), and the thinking budget (tokens per call). Instance limits (topic 1) cap the worst case.

---

## Teardown

Nothing in this module bills by the hour, but the service was public (anyone with its URL could cause Gemini calls), so it
was deleted as soon as the walkthrough was done. Before deleting, what each resource contained was checked, so that only
this module's things were removed: the image repositories held only `moderaai` images, exactly one API key matched by name
(the Module 11 Maps key was not touched), and Firestore held only the `moderation_cache` collection.

The slow one goes first, in the background. Delete the gateway, then its config, then the API (took 2 min 9 s in total,
against 10 min 41 s to create):

```bash
gcloud api-gateway gateways delete moderaai-gateway --location=us-central1 --project=gcp-fde-project --quiet
gcloud api-gateway api-configs delete moderaai-config --api=moderaai-api --project=gcp-fde-project --quiet
gcloud api-gateway apis delete moderaai-api --project=gcp-fde-project --quiet
```

The CI/CD pieces (the GitHub connection is deleted after the repo link), then the service:

```bash
gcloud builds triggers delete moderaai-deploy-trigger --region=us-central1 --project=gcp-fde-project --quiet
gcloud builds repositories delete gcp-modules --connection=moderaai-github --region=us-central1 --project=gcp-fde-project --quiet
gcloud builds connections delete moderaai-github --region=us-central1 --project=gcp-fde-project --quiet
gcloud run services delete moderaai --region=us-central1 --project=gcp-fde-project --quiet     # all 11 revisions
```

The API key is deleted by its exact resource name, so the other key cannot be hit by mistake:

```bash
KEYNAME=$(gcloud services api-keys list --project=gcp-fde-project --filter='displayName="ModeraAI API Key"' --format="value(name)")
gcloud services api-keys delete "$KEYNAME" --project=gcp-fde-project --quiet
```

Data, images and identity:

```bash
gcloud firestore databases delete --database="(default)" --project=gcp-fde-project --quiet
gcloud artifacts repositories delete moderaai-repo --location=us-central1 --project=gcp-fde-project --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location=us-central1 --project=gcp-fde-project --quiet

for role in roles/aiplatform.user roles/datastore.user; do
  gcloud projects remove-iam-policy-binding gcp-fde-project \
    --member="serviceAccount:moderaai-sa@gcp-fde-project.iam.gserviceaccount.com" --role="$role" --condition=None
done
gcloud iam service-accounts delete moderaai-sa@gcp-fde-project.iam.gserviceaccount.com --project=gcp-fde-project --quiet

# the role granted to Cloud Build's own service agent in topic 3
gcloud projects remove-iam-policy-binding gcp-fde-project \
  --member="serviceAccount:service-1039893753206@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin" --condition=None
```

### Gotcha: deleting the GitHub connection leaves its secret behind

The connection stored GitHub's token in Secret Manager, and deleting the connection did not remove it:

```bash
gcloud secrets list --project=gcp-fde-project                                   # moderaai-github-github-oauthtoken-ca5736
gcloud secrets delete moderaai-github-github-oauthtoken-ca5736 --project=gcp-fde-project --quiet
```

The GitHub side is separate: the Cloud Build GitHub App stays installed on the GitHub account until it is removed at
https://github.com/settings/installations.

### Verify it is gone

Every list came back empty, rather than trusting that `delete` succeeded:

```bash
gcloud run services list --region=us-central1 --project=gcp-fde-project                # Listed 0 items.
gcloud api-gateway gateways list --location=us-central1 --project=gcp-fde-project      # Listed 0 items.
gcloud api-gateway apis list --project=gcp-fde-project                                 # Listed 0 items.
gcloud builds triggers list --region=us-central1 --project=gcp-fde-project             # Listed 0 items.
gcloud builds connections list --region=us-central1 --project=gcp-fde-project          # Listed 0 items.
gcloud artifacts repositories list --project=gcp-fde-project                           # Listed 0 items.
gcloud firestore databases list --project=gcp-fde-project                              # Listed 0 items.
gcloud secrets list --project=gcp-fde-project                                          # Listed 0 items.
gcloud services api-keys list --project=gcp-fde-project --format="value(displayName)"  # module-11-maps-key only
```

The `moderaai-api-...cloud.goog` service was no longer enabled, no role bindings remained for `moderaai-sa`, and both
public addresses returned Google's generic 404.

**Left alone on purpose:** the Module 11 Maps key, the enabled APIs (including Secret Manager, which this module turned
on), the retained Cloud Logging entries, and the shared Cloud Build source bucket `gcp-fde-project_cloudbuild`
(8 archives, 17 MB, used by earlier modules too). The build uploads in topic 2 sent the whole repo, so its archives
contain this repo's files, though never `.env` or tokens.
