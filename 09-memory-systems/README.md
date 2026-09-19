# Code — Module 9: Memory Systems

By default an LLM forgets everything when a conversation ends. This module gives an agent memory: what it said a moment ago, what it knows about a returning customer, and past cases it can find by meaning, backed by real GCP services (Redis, Firestore, Cloud SQL). The main track is **SupportBot**, an AI customer support agent, taught as 8 notebooks in [`customer_support_agent/`](customer_support_agent/README.md).

## Layout

```
09-memory-systems/
├── customer_support_agent/    the main track: 8 SupportBot notebooks + setup.py
├── docs/                      the lessons: 8 original topics, plus the SupportBot versions
├── commands.md                every gcloud command run, with real values
├── PROJECT_NOTES.md           what the memory can and can't do, and the links used
├── bat-files/                 the original Windows .bat provisioning scripts, kept for reference
├── deleteds/                  the original generic .py lessons, parked (see its README)
├── requirements.txt
└── .env.example
```

The generic `.py` lessons in `deleteds/` teach the same 8 topics with placeholder data. The notebooks replace them, so each lesson runs once, not twice. Nothing was deleted.

## Setup (do this once)

All infrastructure is created with `gcloud` commands: see [`commands.md`](commands.md). The `.bat` scripts in `bat-files/` are the Windows-only originals of the same commands.

```bash
cp .env.example .env
# ...set PROJECT_ID and a real CLOUD_SQL_PASSWORD (commands.md shows how to generate one)
sed -i '' 's/\r$//' .env          # only if the file has Windows line endings: see the note below
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
gcloud auth application-default login
./.venv/bin/python customer_support_agent/setup.py     # prints "setup OK"
```

**Line endings matter.** If `.env` has Windows (CRLF) line endings, `source .env` leaves a hidden character on every value and `gcloud` rejects the resource names. `commands.md` has the details.

## What each notebook needs

| Notebook | Teaches | Needs |
|---|---|---|
| `01_short_term_memory` | The live chat window | nothing |
| `02_long_term_memory` | Remembering across sessions (a local file) | nothing |
| `03_semantic_memory` | Finding a similar past ticket by meaning | Vertex AI embeddings |
| `04_redis_memory` | Live session state with a TTL | Redis + bastion VM + SSH tunnel |
| `05_firestore_memory` | The durable customer profile | a Firestore database |
| `06_cloud_sql_memory` | Structured ticket history, with a JOIN | Cloud SQL |
| `07_hybrid_memory` | Live session + known profile in one context | Redis + Firestore |
| `08_conversation_memory` | The `SupportAgentMemory` class, then a real Gemini call that uses it | Redis + Firestore + Gemini |

Notebooks 1, 2, 3 and 5 can run as soon as `.env` is filled in. Start Cloud SQL and Redis first, since they take a few minutes (sometimes far longer), and do those four while you wait.

## Try it

Run any notebook from `customer_support_agent/`:

```bash
cd customer_support_agent
../.venv/bin/jupyter nbconvert --to notebook --execute --inplace 03_semantic_memory.ipynb
```

Or open them in VS Code or Jupyter and run cell by cell. The best one to watch is **notebook 8**: its last two cells ask Gemini the same question twice, once with no memory and once in a brand-new chat session with memory. The first answer asks for a ticket number. The second names the settings crash the customer reported earlier, which only the Firestore profile knew.

## Redis: one trap worth knowing

The tunnel to Redis uses a local port. If something on your machine already listens on 6379 (a local Redis is common), the tunnel fails to bind but keeps running, and your code quietly talks to the *local* Redis. Use another port such as 6380 and set `REDIS_PORT=6380` in `.env`. `commands.md` shows how to prove you reached Memorystore.

## Cost note

Firestore is free at this scale. Memorystore and Cloud SQL are **not**: they bill by the hour for as long as they exist (roughly $0.12/hour together), trial credit or not. Delete them when you finish: the teardown commands are at the end of `commands.md`.
