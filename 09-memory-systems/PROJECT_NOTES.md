# Module 9 — Project notes: SupportBot's memory

## What it is

A set of memory building blocks for an AI customer support agent (SupportBot),
each backed by the GCP service that suits it. Together they answer the question a
plain LLM can't: *who is this customer, what did they just say, and what have we
seen before?* Gemini (`gemini-2.5-flash`) does the talking. Memory decides what
it gets to know.

## What it can do

Every row below was run for real on GCP and checked a second way (see
`commands.md`).

| Memory | Backed by | What it does | Lives how long |
|---|---|---|---|
| **Short-term** (`SupportChatMemory`) | a Python list | Keeps the last 8 turns of the current chat; older turns drop off | until the process ends |
| **Long-term (simple)** | a local JSON file | Remembers facts about a customer across restarts | forever, on this machine only |
| **Semantic** | Vertex AI `text-embedding-005` (768-dim vectors) | Finds the most similar past ticket by meaning, e.g. "the app won't sync my files" finds "Sync feature fails after update" (0.77) with almost no shared words | recomputed each run, not stored |
| **Session** | Memorystore Redis | Holds the live chat transcript per session, with a 30-minute TTL | 30 minutes, then it expires by itself |
| **Profile** | Firestore | The durable customer record: plan tier, contact preference, known issues; new issues are appended without overwriting | forever |
| **Ticket history** | Cloud SQL (Postgres) | Customers and tickets in related tables, so you can JOIN, e.g. average resolution time per customer (Acme Corp 7.0 h, Small Biz Co 1.0 h) | forever |
| **Hybrid** (`get_support_context`) | Redis + Firestore | One combined view of "the current chat" plus "what we already know" | as above |
| **`SupportAgentMemory`** | Redis + Firestore | The class an agent calls: `remember_turn`, `remember_fact`, `recall` | as above |

**The proof, in notebook 8.** The same question ("is the crash I reported earlier
still being looked into?") goes to Gemini twice. With no memory it asks the
customer for a ticket number and details. In a brand-new chat session with
memory it names the settings crash, which came only from the Firestore profile
written earlier. The memory outlived the conversation.

## What it can't do (yet)

- **Decide what is worth remembering.** Nothing extracts facts from a chat
  automatically. `remember_fact` is called explicitly, and the capstone only
  stores `known_issues`.
- **Tell "no match" from a match.** `find_similar_ticket` always returns its best
  result. An unrelated question ("what is the weather in Paris") still returns a
  ticket, at a score of about 0.27 against 0.77 for a real match. A real system
  needs a score threshold.
- **Keep embeddings.** The semantic archive is rebuilt in memory every run,
  which means one embedding call per ticket. There is no vector database.
- **Cap a session.** The Redis transcript grows with every turn until its TTL
  expires; nothing trims it or summarises it.
- **Protect customers from each other.** Any code with the project's credentials
  reads every profile and ticket. There is no per-customer access control, and
  the data is stored as plain text. The sample data is invented.
- **Handle more than the demo scenario.** One imagined support product, sample
  customers `cust_042`, `Acme Corp` and `Small Biz Co`, and a handful of tickets.

## Good to know

- **Redis is private.** Memorystore has no public IP, so a bastion VM and an SSH
  tunnel are needed. If a local Redis already owns port 6379, the tunnel silently
  fails to bind and your code talks to the local one instead. It nearly happened
  on this run; the server version (8.6.1 against Memorystore's 7.0) gave it away.
  Details and the check are in `commands.md`.
- **It costs while it exists.** Cloud SQL and Redis have no free tier (roughly
  $0.12 per hour together). Firestore is free at this scale. Delete them when you
  finish.
- **Provisioning time varies a lot.** About 3.5 minutes each on this run, against
  42 and 55 minutes for the same commands on 2026-09-16.
- **The course files use Windows line endings.** That breaks `source .env` on
  macOS and Linux (hidden `\r` on every value). Convert `.env`, `.env.example` and
  `requirements.txt` to Unix endings; leave the `.bat` files alone.
- **Two sets of data can coexist.** The parked generic lessons and the SupportBot
  notebooks use different collection, table and key names on purpose.

## Links used

**GitHub**

- Repository: https://github.com/AnjaniMalhotra/gcp-modules
- This module's branch: https://github.com/AnjaniMalhotra/gcp-modules/tree/09-memory-systems

**What the code talks to** (through the Google client libraries)

- Vertex AI, for Gemini and embeddings: https://aiplatform.googleapis.com
- Firestore: https://firestore.googleapis.com
- Cloud SQL Admin API (the Python Connector uses it): https://sqladmin.googleapis.com
- Memorystore for Redis (provisioning only): https://redis.googleapis.com
- Compute Engine, for the bastion VM: https://compute.googleapis.com
- Redis itself is reached through the SSH tunnel at `localhost:6380`, not over the internet.

**Where to look at the resources in the Cloud Console** (standard pages; not
opened during this run, since everything was checked from the CLI)

- Cloud SQL: https://console.cloud.google.com/sql/instances?project=gcp-fde-project
- Memorystore: https://console.cloud.google.com/memorystore/redis/instances?project=gcp-fde-project
- VMs: https://console.cloud.google.com/compute/instances?project=gcp-fde-project
- Firestore: https://console.cloud.google.com/firestore/databases?project=gcp-fde-project

## Where to look next

- [`README.md`](README.md): layout, setup, and how to run it
- [`commands.md`](commands.md): every `gcloud` command run, with real values
- [`customer_support_agent/`](customer_support_agent/README.md): the 8 notebooks
- [`docs/`](docs/): the lessons
- [`deleteds/README.md`](deleteds/README.md) and [`bat-files/README.md`](bat-files/README.md): the parked and Windows files
