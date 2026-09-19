# Module 9 — Project notes: SupportBot's memory

## What it is

A set of memory building blocks for an AI customer support agent (SupportBot),
each backed by the GCP service that suits it. Together they answer the question a
plain LLM can't: *who is this customer, what did they just say, and what have we
seen before?* Gemini (`gemini-2.5-flash`) does the talking. Memory decides what
it gets to know.

## The 8 lessons at a glance

All 8 notebooks ran for real on GCP with no errors, and their outputs are saved
inside them. Three are kinds of memory, three are places to store it, and two
combine them. Only the SupportBot notebooks were run in full.

| # | Lesson | Kind | Backed by | Lives how long | Notebook |
|---|---|---|---|---|---|
| 1 | Short-term | memory | a Python list | until the program ends | `01_short_term_memory` |
| 2 | Long-term | memory | a local JSON file | forever, on one machine | `02_long_term_memory` |
| 3 | Semantic | memory | Vertex AI embeddings (`text-embedding-005`) | rebuilt each run, never stored | `03_semantic_memory` |
| 4 | Session | storage | Memorystore Redis | 30 minutes, then it expires | `04_redis_memory` |
| 5 | Profile | storage | Firestore | forever | `05_firestore_memory` |
| 6 | Ticket history | storage | Cloud SQL (Postgres) | forever | `06_cloud_sql_memory` |
| 7 | Hybrid | combination | Redis + Firestore | as above | `07_hybrid_memory` |
| 8 | Conversation memory | capstone | Redis + Firestore + Gemini | as above | `08_conversation_memory` |

## A tiny example of each, in plain words

The story is one customer, `cust_042`, talking to SupportBot. The numbers are the
real ones we got.

1. **Short-term.** The customer writes "My app keeps crashing", then "It happens
   when I open settings." SupportBot only understands "It" because it still has
   the first message. It keeps the last 8 messages, so in a long chat the oldest
   fall away. We watched the first two disappear.
2. **Long-term.** Last week SupportBot wrote down "on the Enterprise plan" and "had
   a billing issue resolved on Jan 5". We pretended the program restarted, and it
   read both facts back from a file. A fact written down survives the program
   closing.
3. **Semantic.** The customer writes "the app won't sync my files." SupportBot
   finds the old ticket "Sync feature fails after update", though the words
   differ. It scored 0.77, against about 0.55 to 0.59 for the others. Ask about the
   weather and everything scores about 0.27: nothing matches.
4. **Redis.** During a chat, SupportBot keeps the transcript under
   `support_session:sess_8842:turns` and sets it to expire in 30 minutes, like a
   whiteboard wiped after the call. We read it back with 1799 seconds left.
5. **Firestore.** The customer's file: plan Enterprise, prefers email, known
   issues. A new issue ("App crashes on opening settings") is added to the list
   without erasing anything else.
6. **Cloud SQL.** Two tables, customers and tickets. Ask "how long do tickets take
   to fix, per customer?" and the database joins them: Acme Corp's took 2 and 12
   hours (average 7.0), Small Biz Co's took 1.
7. **Hybrid.** The customer writes "Still crashing, same issue as before." Redis
   supplies the current chat and Firestore supplies the file, so SupportBot can
   tell "same issue as before" means the settings crash.
8. **Conversation memory.** One helper, `SupportAgentMemory`, wraps 4, 5 and 7 into
   three actions: remember a message, remember a fact, recall everything. In a
   brand-new chat the customer asks "is the crash I reported earlier still being
   looked into?" With no memory the bot asks for a ticket number. With memory it
   names the settings crash. That is the proof the memory outlives the conversation.

## See it, and question it

**Ask it your own questions.** Notebook 8, in the cells after "Now actually give
it to the model": change the `question` line and re-run. It needs Redis and
Firestore running, which are deleted right now. Recreating them takes about 5
minutes (`commands.md`).

**Or try it without recreating anything.** The model only ever receives a block of
text, so you can reproduce what notebook 8 sends it. This is the notebook's real
prompt and the exact facts the customer's file held. Save it as a file inside
`customer_support_agent/` (say `try_it.py`) and run
`../.venv/bin/python try_it.py`, or paste it into a notebook cell in that folder.
It has to live there so that `from setup import ...` finds `setup.py`. Change the
questions at the bottom to try your own:

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

The first and third answers each show a limit; see "What it can't do" below.

## Where to watch each memory in the Google Cloud Console

There is **no single screen** that shows all the memories. These are the standard
Console pages, not opened during this run (everything was checked from the command
line), and they are empty right now because the resources were deleted.

| Memory | Open this | What you'll see | What you won't |
|---|---|---|---|
| **Profile** (Firestore) | https://console.cloud.google.com/firestore/databases?project=gcp-fde-project, then the `(default)` database, Data tab | The actual documents: open `support_customer_profiles`, then `cust_042` | nothing hidden |
| **Ticket history** (Cloud SQL) | https://console.cloud.google.com/sql/instances?project=gcp-fde-project, then the instance, then **Cloud SQL Studio** | Log in as `postgres` and run `SELECT * FROM support_tickets;` to see the rows | a table browser without logging in |
| **Session** (Redis) | https://console.cloud.google.com/memorystore/redis/instances?project=gcp-fde-project, then the instance | Health and graphs: memory used, connections | **The keys.** Open the tunnel and use the "See what is stored in Redis" snippet in `commands.md` |
| **By meaning** (embeddings) | https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/metrics?project=gcp-fde-project | How many Vertex AI requests were made | The vectors: they are never stored |
| **Graphs for all of these** | https://console.cloud.google.com/monitoring/metrics-explorer?project=gcp-fde-project | Chart the numbers of any service above | the data inside them |

Short-term memory and the simple long-term file live only in the program and on
this laptop, so the Console can't show them. The notebooks' saved outputs are where
you see those.

## What it can't do (yet)

- **Decide what is worth remembering.** Nothing extracts facts from a chat
  automatically. `remember_fact` is called explicitly, and the capstone only
  stores `known_issues`.
- **Tell "no match" from a match.** `find_similar_ticket` always returns its best
  result. An unrelated question still returns a ticket, at about 0.27 against 0.77
  for a real match. A real system needs a score threshold.
- **Avoid over-reassuring.** Told only that a crash was *reported*, it answered
  "Yes" to "is it being looked into?". Nothing checks its answers against the
  facts, and on the notebook run it answered more carefully.
- **Show the plan in the capstone.** `SupportAgentMemory.recall()` passes only
  known issues, so the bot says it doesn't know the plan even though Firestore has
  it (lesson 7's version includes it). The fix is one line, not made.
- **Cap a session.** The Redis transcript grows until its TTL expires; nothing
  trims or summarises it.
- **Protect customers from each other.** Any code with the project's credentials
  reads every profile and ticket. There is no per-customer access control, and the
  data is plain text. The sample data is invented.

## Good to know

- **Redis is private, and a local Redis can fool you.** Memorystore has no public
  IP, so a bastion VM and an SSH tunnel are needed. If a Redis on your own machine
  already owns port 6379, the tunnel silently fails to bind and your code talks to
  the local one. It nearly happened here; the server version (8.6.1 against
  Memorystore's 7.0) gave it away. The check is in `commands.md`.
- **It costs while it exists.** Cloud SQL and Redis have no free tier (roughly
  $0.12 per hour together). Firestore is free at this scale.
- **Provisioning time varies a lot.** About 3.5 minutes each on this run, against
  42 and 55 minutes for the same commands on 2026-09-16.
- **The course files use Windows line endings.** That breaks `source .env` on
  macOS and Linux. Convert `.env`, `.env.example` and `requirements.txt` to Unix
  endings; leave the `.bat` files alone.

## Links

- Repository: https://github.com/AnjaniMalhotra/gcp-modules
- This module's branch: https://github.com/AnjaniMalhotra/gcp-modules/tree/09-memory-systems
- The Console pages for watching the memories are in the section above.
