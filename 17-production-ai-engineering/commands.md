# Module 17 — GCP CLI Commands

Every step for this module, done with `gcloud` (and `curl`) only, exactly as it was run on
2026-09-20. These replace the Windows-only `.bat` scripts, which are kept unchanged in
[`bat-files/`](bat-files/) for reference. Nothing in this module needs a password; the only
secret is the API key created in topic 9, which stays in the gitignored `.env`.

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

Python environment for the local test scripts (`load_test.py`, `10_cost_comparison_demo.py`):

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
`09_openapi_spec.yaml`).

### Gotcha 2: 50 requests do not scale it up as shipped

The first load test (`python load_test.py --url $SERVICE_URL --requests 50`) succeeded 50/50, but **all 50 were
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
