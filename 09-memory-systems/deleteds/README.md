# deleteds/

Parked, not deleted. These are the original generic lessons: the same 8 memory
topics as the SupportBot notebooks in `../customer_support_agent/`, taught with
placeholder data. The notebooks replace them, so each topic runs once instead of
twice. Nothing else in the module imports them. Delete the folder when you're
sure you don't want it (`git rm -r deleteds/`).

| File | What it was |
|---|---|
| `setup.py` | Was `00_setup.py`: shared config plus Gemini and Firestore clients. Renamed because the scripts do `from setup import ...`, which can't find a file called `00_setup.py` |
| `01_short_term_memory.py` | Sliding-window memory in a Python list |
| `02_long_term_memory.py` | Memory in a local JSON file |
| `03_semantic_memory.py` | Embeddings and cosine similarity |
| `04_redis_memory.py` | Redis through the SSH tunnel |
| `05_firestore_memory.py` | Firestore documents |
| `06_cloud_sql_memory.py` | Cloud SQL through the Python Connector |
| `07_hybrid_memory.py` | Redis + Firestore combined |
| `08_conversation_memory.py` | A `ConversationMemory` class |

## Running one anyway

They still run, from the module root or from this folder (checked with 01 and 03):

```bash
./.venv/bin/python deleteds/03_semantic_memory.py
```

`04`, `07` and `08` hardcode `localhost:6379` for Redis, so if a local Redis owns that port, edit the port in the script (see `../commands.md`). `02` writes `long_term_memory.json` into the folder you run it from (gitignored), and `05`, `07` and `08` write to the `long_term_memory` Firestore collection.
