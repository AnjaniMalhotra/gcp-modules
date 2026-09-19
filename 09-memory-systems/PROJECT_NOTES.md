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

## Did we build all 8?

Yes. Each of the 8 lessons has a notebook that ran for real on GCP, with no
errors, and its output is saved inside the notebook. They aren't 8 of the same
thing, though: three are kinds of memory, three are places to store memory, and
two combine them.

| # | Lesson | What kind of thing | Notebook | Where the data lived |
|---|---|---|---|---|
| 1 | Short-term | a kind of memory | `01_short_term_memory` | inside the program only |
| 2 | Long-term | a kind of memory | `02_long_term_memory` | a local file (a simple stand-in; lesson 5 does it properly) |
| 3 | Semantic | a kind of memory | `03_semantic_memory` | rebuilt in memory each run (the embeddings themselves are real, from Vertex AI) |
| 4 | Redis | a place to store it | `04_redis_memory` | Memorystore Redis |
| 5 | Firestore | a place to store it | `05_firestore_memory` | Firestore |
| 6 | Cloud SQL | a place to store it | `06_cloud_sql_memory` | Cloud SQL |
| 7 | Hybrid | a combination | `07_hybrid_memory` | Redis + Firestore |
| 8 | Conversation memory | the capstone combination | `08_conversation_memory` | Redis + Firestore + Gemini |

Only the SupportBot notebooks were run in full. The parked generic scripts in
`deleteds/` were tried only for lessons 1 and 3.

## A tiny example of each, in plain words

The story is one customer, `cust_042`, talking to SupportBot. The numbers below
are the real ones we got.

1. **Short-term.** The customer writes "My app keeps crashing", then "It happens
   when I open settings." SupportBot only understands "It" because it still has
   the first message. It keeps the last 8 messages, so if the chat goes on long
   enough the oldest ones fall away. We watched the first two disappear.
2. **Long-term (simple).** Last week SupportBot wrote down: "on the Enterprise
   plan" and "had a billing issue resolved on Jan 5". We pretended the program
   restarted, and it read those two facts back from a file. A fact written down
   survives the program closing.
3. **Semantic.** The customer writes "the app won't sync my files." SupportBot
   searches old tickets and finds "Sync feature fails after update", even though
   the words are different. The match scored 0.77, against about 0.55 to 0.59 for
   the others. Ask about the weather and everything scores about 0.27: nothing
   matches.
4. **Redis.** While a chat is happening, SupportBot keeps the transcript under
   `support_session:sess_8842:turns` and sets it to expire in 30 minutes, like a
   whiteboard wiped after the call. We read it back with 1799 seconds left.
5. **Firestore.** The customer's file: plan Enterprise, prefers email, known
   issues. When a new issue comes in ("App crashes on opening settings") it is
   added to the list without erasing anything else in the file.
6. **Cloud SQL.** Two tables, customers and tickets. Ask "how long do tickets take
   to fix, per customer?" and the database joins them: Acme Corp's tickets took 2
   and 12 hours (average 7.0), Small Biz Co's took 1 hour.
7. **Hybrid.** The customer writes "Still crashing, same issue as before."
   Redis supplies the current chat and Firestore supplies the file. With both,
   SupportBot can tell that "same issue as before" means the settings crash.
8. **Conversation memory.** One helper, `SupportAgentMemory`, wraps 4, 5 and 7 into
   three actions: remember a message, remember a fact, recall everything. In a
   brand-new chat the customer asks "is the crash I reported earlier still being
   looked into?" With no memory the bot asks for a ticket number. With memory it
   names the settings crash.

## See it, and question it

**Ask it your own questions.** The place to do that is notebook 8, in the cells
after "Now actually give it to the model". Change the `question` line and re-run
those cells. It needs Redis and Firestore running, which are deleted right now:
recreating them takes about 5 minutes (`commands.md`).

**Or try it without recreating anything.** The model only ever receives a block of
text, so you can reproduce what notebook 8 sends it. This is the notebook's
real prompt and the exact facts the customer's file held. Save it as a file
inside `customer_support_agent/` (say `try_it.py`) and run
`../.venv/bin/python try_it.py`, or paste it into a notebook cell in that folder.
It has to live there so that `from setup import ...` finds `setup.py`. Change
the questions at the bottom to try your own:

```python
from setup import genai_client, MODEL_FLASH

known_issues = ['Billing issue resolved Jan 5', 'App crashes on opening settings - reported today']

def ask(question):
    context = f"Current chat:\ncustomer: {question}\n\nKnown issues: {known_issues}"
    prompt = ("You are SupportBot, a customer support agent. Reply directly to the customer's latest "
              "message, in the first person, using ONLY the facts below. Never mention 'memory' or "
              "'context'. If the facts don't cover something, say you don't have that information yet.\n\n" + context)
    return genai_client.models.generate_content(model=MODEL_FLASH, contents=prompt).text.strip()

for q in ["Was my billing problem from January sorted out?", "What is your refund policy?"]:
    print(f"Q: {q}\nA: {ask(q)}\n")
```

What we got when we asked four questions that way:

| You ask | SupportBot answers |
|---|---|
| "Hi, is the crash I reported earlier still being looked into?" | "Yes, the issue with the app crashing on opening settings was reported today." |
| "Was my billing problem from January sorted out?" | "Yes, your billing issue was resolved on January 5." |
| "What plan am I on?" | "I don't have that information yet." |
| "What is your refund policy?" | "I don't have that information yet." |

Two of those are worth reading closely, because they show the limits:

- **It can sound surer than it should.** The first answer says "Yes", but the
  file only says the crash was *reported*. Nobody wrote down that anyone is looking
  into it. On the notebook run it answered more carefully, so the same setup can
  give different answers on different runs.
- **It says it doesn't know the plan, but the plan is in Firestore.** The
  capstone's `recall()` passes only the known issues, not the plan tier
  (lesson 7's version does include it). The fix is one line. It was not made.

## Where to watch each memory in the Google Cloud Console

There is **no single screen** that shows all the memories: two of them aren't in
the cloud at all, and Redis hides its contents. Here is where each one can be seen.
These are the standard Console pages; they were not opened during this run,
since everything was checked from the command line. They are all empty right now
because the resources were deleted at the end of the module.

| Memory | Open this | What you'll see | What you won't |
|---|---|---|---|
| **Profile** (Firestore) | https://console.cloud.google.com/firestore/databases?project=gcp-fde-project, then the `(default)` database, Data tab | The actual documents: open `support_customer_profiles`, then `cust_042` | nothing hidden here |
| **Ticket history** (Cloud SQL) | https://console.cloud.google.com/sql/instances?project=gcp-fde-project, then the instance, then **Cloud SQL Studio** | Log in as `postgres` and run `SELECT * FROM support_tickets;` to see the rows | a table browser without logging in |
| **Session** (Redis) | https://console.cloud.google.com/memorystore/redis/instances?project=gcp-fde-project, then the instance | Health and graphs: memory used, connections | **The keys themselves.** To read them, open the tunnel and use the "See what is stored in Redis" snippet in `commands.md` |
| **The machine used to reach Redis** | https://console.cloud.google.com/compute/instances?project=gcp-fde-project | Whether the helper VM is running | |
| **By meaning** (embeddings) | https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/metrics?project=gcp-fde-project | How many Vertex AI requests were made | The vectors: they are never stored |
| **Graphs for all the services in one place** | https://console.cloud.google.com/monitoring/metrics-explorer?project=gcp-fde-project | Pick any of the services above and chart its numbers | the data inside them |

Short-term memory and the simple long-term file live only in the program and on
this laptop, so the Console can't show them. The notebooks' saved outputs are
where you see those.

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
- **Promise not to over-reassure.** Told only that a crash was reported, it
  answered "Yes" to "is it being looked into?". Nothing checks its answers against
  the facts.
- **Show the plan in the capstone.** `SupportAgentMemory.recall()` passes only
  known issues, so the bot says it doesn't know the plan even though Firestore
  has it.
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

**Console pages for watching the memories** are in the section "Where to watch each memory in the Google Cloud Console" above.

## Where to look next

- [`README.md`](README.md): layout, setup, and how to run it
- [`commands.md`](commands.md): every `gcloud` command run, with real values
- [`customer_support_agent/`](customer_support_agent/README.md): the 8 notebooks
- [`docs/`](docs/): the lessons
- [`deleteds/README.md`](deleteds/README.md) and [`bat-files/README.md`](bat-files/README.md): the parked and Windows files
