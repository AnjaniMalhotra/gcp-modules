# Teacher Plan — Module 9: Memory Systems

**Total time:** 3 hrs (180 min) — includes ~25 min buffer, larger than usual because two topics involve real infrastructure provisioning with unpredictable timing.
**Format this module:** mixed — pure Python for concepts (1, 2, 3), `.bat` provisioning + Python for storage backends (4, 5, 6), pure Python again for the combined topics (7, 8).

## Before you start recording/teaching

- [ ] Modules 2 and 3 complete, `.env` filled in for this module
- [ ] **Kick off Cloud SQL instance creation BEFORE you start recording**, or right at the start of topic 4 — instance creation takes 5-10 minutes and you do not want to sit there waiting on camera. By the time you reach topic 6, it'll be ready.
- [ ] Two Command Prompt windows ready (one for the SSH tunnel, one for everything else) — needed from topic 4 onward
- [ ] `code/09-memory-systems/99_cleanup.bat` open and ready to run at the very end — do not skip this, Redis and Cloud SQL both bill hourly

## Suggested pacing (180 min)

| # | Topic | Minutes | Format |
|---|-------|---------|--------|
| 1 | Short-Term Memory | 16 | Talk + Python demo |
| 2 | Long-Term Memory | 14 | Talk + Python demo |
| 3 | Semantic Memory | 18 | Talk + Python demo |
| 4 | Redis | 26 | Provision + SSH tunnel + Python demo (most setup-heavy topic) |
| 5 | Firestore | 16 | Python demo only, no provisioning wait |
| 6 | Cloud SQL | 22 | Python demo (instance already provisioned in background since topic 4) |
| 7 | Hybrid Memory | 18 | Python demo combining 4 + 5 |
| 8 | Conversation Memory | 22 | Capstone class + demo |
| — | Cleanup + recap + buffer | 28 | Run `99_cleanup.bat` live, rapid-fire Q&A |

## Teaching order rationale

Keep the syllabus order. Topics 1-3 build the mental model (what kinds of memory exist) with zero infrastructure — nothing to provision, nothing to break. Topics 4-6 are the storage backends, in an order that happens to work well operationally: kick off the *slowest* provisioning step (Cloud SQL) at the start of topic 4, let it run in the background through topics 4 and 5, and it's ready right when topic 6 needs it. Topics 7-8 recombine everything into something reusable.

## Per-Component Focus

### 1. Short-Term Memory
**Land this one idea:** "This is just a Python list — and that's the whole point. Short-term memory doesn't need to be fancy, it needs to be fast and disposable."
- Demo: a sliding-window memory class, push past its limit, watch the oldest turn silently drop.
- Common confusion: students expect "short-term" to mean a specific technology. It doesn't — it's a *lifespan* concept (dies with the process), not a storage choice.

### 2. Long-Term Memory
**Land this one idea:** "The only difference from topic 1 is: does it survive a restart?"
- Demo: write memories to a local JSON file, "restart" by reading fresh from disk instead of from the in-memory list.
- Common confusion: conflating "long-term" with "semantic" — clarify long-term is about *durability*, semantic (next topic) is about *how you search it*. They're independent properties, often combined.

### 3. Semantic Memory
**Land this one idea:** "Same embeddings idea from Module 3, applied to memories instead of arbitrary text — recall by meaning, not exact wording."
- Demo: store 3 memories as vectors, query with a rephrased question, show it finds the right one despite no shared words.
- Explicitly call out: this code is written fresh here, not imported from Module 3 — every module in this course stands alone.
- Common confusion: students think this replaces topics 1/2. It doesn't — semantic search is a *retrieval method*, layered on top of long-term storage, not a replacement for it.

### 4. Redis
**Land this one idea:** "Redis is fast because it's private — and private means your laptop can't reach it directly. That's not a bug, that's the security model."
- This is the most operationally complex topic in the module — budget real time.
- Demo sequence: run `04a_provision_redis_and_bastion.bat` → open a **second** Command Prompt window → paste the SSH tunnel command (the internal Redis IP printed by the provisioning script) → back in the first window, run `04_redis_memory.py` against `localhost` → point out it's really talking to Redis, just through the tunnel.
- Common confusion: students try to connect directly to the Redis instance's IP from their laptop and get a timeout. Use this as a live "let's see what happens" moment before showing the tunnel — the failure makes the lesson stick.

### 5. Firestore
**Land this one idea:** "No provisioning step, no bill, no bastion — this is the easy one, enjoy it."
- Demo: straight to Python, write a memory document, read it back.
- Good moment to explicitly contrast with topic 4's complexity — reinforces *why* the extra Redis setup was worth understanding.

### 6. Cloud SQL
**Land this one idea:** "Structured, relational, and — unlike Redis — reachable from your laptop without a bastion, because Cloud SQL ships a secure connector built for exactly this."
- By now the instance (kicked off back in topic 4) should be ready — confirm live with `gcloud sql instances describe`.
- Demo: connect via `cloud-sql-python-connector`, insert a memory row, query it back.
- Common confusion: students expect Cloud SQL to need the same bastion-VM dance as Redis. Explicitly name why it doesn't — the Cloud SQL Auth Proxy/Connector handles secure connection over the public internet using IAM, which Memorystore has no equivalent for.

### 7. Hybrid Memory
**Land this one idea:** "Real agents don't pick ONE memory type — short-term in Redis, long-term in Firestore, working together."
- Demo: one script, one function that writes to both, one that reads from both and merges the result.
- Common confusion: students think "hybrid" means one database doing two jobs. It means two *different* databases, each doing the job they're best at.

### 8. Conversation Memory
**Land this one idea:** "This is what topics 1 through 7 were building toward — a class an actual agent could import and call."
- Demo: a `ConversationMemory` class wrapping topic 7's pattern — `remember()`, `recall()`, a clean interface hiding Redis/Firestore details from whatever agent uses it.
- This is also the natural moment to run `99_cleanup.bat` live and narrate what's being torn down and why.

## Wrap-up

- Run `99_cleanup.bat` on screen — narrate each resource being deleted, tie back to Module 2's Cost Optimization topic
- Rapid-fire recap: one question from each topic's "Quick Recap" (8 questions)
- Homework before whichever module comes next: re-read `.env.example` for this module and understand what each key was for — especially `CLOUD_SQL_PASSWORD`, the first real secret this course has handled
- No "tease next module" here since modules are being built out of order — just confirm what's coming next when it's decided
