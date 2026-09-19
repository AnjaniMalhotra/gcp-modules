# Module 9 — GCP CLI Commands

Every infrastructure step for this module, done with `gcloud` only, exactly as
it was run. These replace the Windows-only `.bat` scripts, which are kept
unchanged in [`bat-files/`](bat-files/) for reference.

Project used throughout:

```
Project name:   GCP FDE Project
Project ID:     gcp-fde-project
Project number: 1039893753206
Region / zone:  us-central1 / us-central1-a
```

**About the database password.** It is a live secret for as long as the
instance exists, so it is never typed into a command. It lives only in the
gitignored `.env`, and the commands below read it from there:
`"$CLOUD_SQL_PASSWORD"` is the value loaded by `set -a && source .env && set +a`.
Everything else below is written with its real value.

---

## 0. Setup

```bash
gcloud config set project gcp-fde-project
gcloud auth application-default login
gcloud auth application-default set-quota-project gcp-fde-project
```

The APIs this module needs were already enabled on the project. Confirm:

```bash
gcloud services list --enabled --project=gcp-fde-project --format="value(config.name)" \
  | grep -E "^(aiplatform|firestore|sqladmin|redis|compute)\."
```

Create `.env`, with a generated database password that is never printed:

```bash
cd 09-memory-systems
cp .env.example .env
PW=$(openssl rand -base64 18 | tr -d '=+/' | cut -c1-20)
sed -i '' -e "s|^PROJECT_ID=.*|PROJECT_ID=gcp-fde-project|" -e "s|^CLOUD_SQL_PASSWORD=.*|CLOUD_SQL_PASSWORD=$PW|" .env
unset PW
```

**Gotcha found on this run: the course files have Windows (CRLF) line endings.**
With CRLF, `source .env` leaves a hidden `\r` on every value, so
`gcloud sql instances create agent-memory-sql` was rejected with `Bad value
[agent-memory-sql]: must be composed of lowercase letters, numbers, and hyphens`,
and Redis with `Permission denied on 'locations/us-central1'` (the region had a
`\r` on it). Nothing was created by either failed attempt. Fix, for the text
config files only (never the `.bat` files, which need CRLF on Windows):

```bash
sed -i '' 's/\r$//' .env .env.example requirements.txt
```

Python environment:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Load the names for the commands below:

```bash
set -a && source .env && set +a
```

---

## Topic 5 — Firestore (no provisioning beyond the database)

The `(default)` database had been deleted at the end of the previous module, so
it was created again. It reported `freeTier: true`.

```bash
gcloud firestore databases create \
  --project=gcp-fde-project \
  --location=us-central1 \
  --type=firestore-native
```

Reading documents back needs the client library (`gcloud firestore` has no
"read documents" command):

```bash
./.venv/bin/python -c "
from google.cloud import firestore
db = firestore.Client(project='gcp-fde-project')
print(db.collection('support_customer_profiles').document('cust_042').get().to_dict())"
```

---

## Topic 6 — Cloud SQL (Postgres)

```bash
gcloud sql instances create agent-memory-sql \
  --project=gcp-fde-project \
  --database-version=POSTGRES_15 \
  --cpu=1 \
  --memory=3840MB \
  --region=us-central1 \
  --storage-size=10GB \
  --storage-type=SSD \
  --root-password="$CLOUD_SQL_PASSWORD"

gcloud sql databases create memory_db \
  --instance=agent-memory-sql \
  --project=gcp-fde-project

gcloud sql instances describe agent-memory-sql --project=gcp-fde-project --format="value(state)"
# -> RUNNABLE
```

**Timing:** ready in about 3.5 minutes on this run. The identical command took
42 minutes in Module 13 three days earlier (2026-09-16), so budget for the slow case.

The notebook connects through the Cloud SQL Python Connector with your ADC
login. No bastion and no public-IP allow-listing.

---

## Topic 4 — Memorystore Redis + bastion VM + SSH tunnel

Memorystore has no public IP, so a small VM inside the same network is the
stepping stone.

```bash
gcloud redis instances create agent-memory-redis \
  --project=gcp-fde-project \
  --size=1 \
  --region=us-central1 \
  --tier=basic \
  --redis-version=redis_7_0

gcloud compute instances create agent-memory-bastion \
  --project=gcp-fde-project \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=debian-12 \
  --image-project=debian-cloud

gcloud redis instances describe agent-memory-redis \
  --project=gcp-fde-project --region=us-central1 --format="value(host)"
# -> 10.223.239.179 on this run (assigned at creation, so it differs each time)
```

**Timing:** ready in about 3.5 minutes on this run (55 minutes in Module 13 on 2026-09-16).

### The tunnel, and the trap that nearly hid the wrong Redis

The documented tunnel uses local port 6379:

```bash
gcloud compute ssh agent-memory-bastion --project=gcp-fde-project --zone=us-central1-a \
  -- -L 6379:10.223.239.179:6379 -N
```

On this machine that **silently failed**. A Redis server was already running on
the laptop and owned port 6379, so ssh printed

```
bind [127.0.0.1]:6379: Address already in use
Could not request local forwarding.
```

but kept running. A PING to `localhost:6379` then succeeded, against the
*local* Redis, and the lessons would have "passed" against the wrong server.
The only giveaway was the version: the server said `8.6.1`, while Memorystore
was created as `REDIS_7_0`. Diagnose with:

```bash
lsof -nP -iTCP:6379 -sTCP:LISTEN
```

Fix: use a different local port, and make ssh fail loudly if the forward can't
be set up (`ExitOnForwardFailure`):

```bash
gcloud compute ssh agent-memory-bastion --project=gcp-fde-project --zone=us-central1-a \
  -- -L 6380:10.223.239.179:6379 -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30
```

The notebooks read the port from `.env` (`REDIS_PORT=6380`). Prove you are on
Memorystore and not a local Redis by writing a marker key through the tunnel and
checking it is absent locally:

```bash
./.venv/bin/python - <<'EOF'
import redis, uuid
tunnel = redis.Redis(host="localhost", port=6380, decode_responses=True)
local  = redis.Redis(host="localhost", port=6379, decode_responses=True)
marker = f"tunnel-check:{uuid.uuid4()}"
print("tunnel version:", tunnel.info()["redis_version"], "| local version:", local.info()["redis_version"])
tunnel.set(marker, "hello", ex=60)
print("marker on local Redis (must be False):", bool(local.exists(marker)))
tunnel.delete(marker)
EOF
# -> tunnel version: 7.0.15 | local version: 8.6.1 | marker on local Redis: False
```

### See what is stored in Redis (the Console can't show keys)

With the tunnel open, list every session key with its length and time left:

```bash
./.venv/bin/python - <<'EOF'
import redis
r = redis.Redis(host="localhost", port=6380, decode_responses=True)
for k in sorted(r.keys("support_session:*")):
    print(k, r.llen(k), "turns, TTL", r.ttl(k), "s")
EOF
# -> support_session:sess_8842:turns 3 turns, TTL 1673 s   (and the other sessions)
```

---

## Running the notebooks

The SupportBot notebooks are in `customer_support_agent/`. Run from there:

```bash
cd customer_support_agent
for nb in 01_short_term_memory 02_long_term_memory 03_semantic_memory 05_firestore_memory \
          04_redis_memory 06_cloud_sql_memory 07_hybrid_memory 08_conversation_memory; do
  ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace $nb.ipynb --ExecutePreprocessor.timeout=240
done
```

Notebooks 1, 2, 3 and 5 need no Redis or Cloud SQL (5 needs the Firestore
database). 4, 7 and 8 need the tunnel. 6 needs Cloud SQL.

Every result was checked a second way, not just read from the notebook:

- **Semantic memory (3):** scored three queries against all three tickets. The
  right ticket won each time (about 0.77 against 0.39 to 0.59), and an unrelated
  weather question scored about 0.27 for all of them, so low scores mean "no
  real match".
- **Cloud SQL (6):** read the raw ticket rows and recomputed the averages in
  Python. Acme Corp `[2.0, 12.0]` gives 7.0 hours and Small Biz Co `[1.0]` gives 1.0, matching
  the SQL `AVG`.
- **Redis (4, 7, 8):** listed the `support_session:*` keys through the tunnel:
  server 7.0.15, three sessions, TTLs near 1800 s.
- **Firestore (5, 7, 8):** read the profile back with a fresh client.
- **Capstone (8):** the same question to Gemini with no memory (it asks for a
  ticket number) and in a brand-new chat session with memory (it names the
  settings crash, which only the Firestore profile knew).

### Other real fixes made on this run

- `from setup import ...` failed for 5 of the 8 notebooks because the file was
  `00_setup.py`. It is now `customer_support_agent/setup.py`.
- The notebook setup loaded `../.env` relative to wherever you ran it. It now
  finds the `.env` next to the module regardless of the working directory.
- `requirements.txt` had no Jupyter, though the main track is notebooks.
- Redis host and port were hardcoded to `localhost:6379`; they are now
  `REDIS_HOST` and `REDIS_PORT` in `.env`.

---

## Teardown

Cloud SQL and Redis (and its bastion VM) have no free tier and bill hourly, so
they are deleted as soon as the lessons have been run and verified. Stop the SSH
tunnel first; deleting the bastion VM out from under it would also kill it.

```bash
pkill -f "6380:10.223.239.179:6379"      # the tunnel started above; leaves any local Redis alone

gcloud sql instances delete agent-memory-sql --project=gcp-fde-project --quiet
gcloud redis instances delete agent-memory-redis --region=us-central1 --project=gcp-fde-project --quiet
gcloud compute instances delete agent-memory-bastion --zone=us-central1-a --project=gcp-fde-project --quiet
```

The Firestore database is free at this scale, but this module created it, so it
was removed with the rest:

```bash
gcloud firestore databases delete --database="(default)" --project=gcp-fde-project --quiet
```

Verify everything is actually gone rather than trusting that `delete` succeeded:

```bash
gcloud sql instances list --project=gcp-fde-project                          # should be empty
gcloud redis instances list --region=us-central1 --project=gcp-fde-project   # should be empty
gcloud compute instances list --project=gcp-fde-project                      # should be empty
gcloud firestore databases list --project=gcp-fde-project                    # should be empty
```

**Confirmed on this run:** all four `list` commands came back empty. Deletion was
also quick this time: both Cloud SQL and Redis were gone within a few minutes
(Redis took over 20 minutes to delete in Module 13). The Maps API key from
Module 11 and a Redis already running on the laptop were left alone.

Google documents that a deleted Cloud SQL instance's name cannot be reused for
a period afterwards (up to about a week). If a re-run fails to create
`agent-memory-sql`, that is the likely reason; pick a new
`CLOUD_SQL_INSTANCE_NAME` in `.env`.
