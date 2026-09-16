# 2. Long-Term Memory

## What Is It? (Plain English)

Long-term memory is anything written somewhere that survives your program stopping and starting again. It's the same idea as short-term memory (topic 1) with one property added: durability.

## Why It Matters for AI Engineers

Users expect an agent to remember them *tomorrow*, not just for the next five minutes. That requires writing memory somewhere outside your program's RAM — a file, a database, anything that's still there after a restart. Topics 5 and 6 cover the real GCP options (Firestore, Cloud SQL); this topic teaches the underlying idea with the simplest possible version: a local file.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Durability** | Whether data survives after the process that wrote it stops running |
| **Persistence** | The general act of writing data somewhere durable |
| **Fact / Memory Record** | One discrete piece of information worth keeping past this session |
| **Read-Modify-Write** | The pattern of loading existing data, adding to it, then saving it back |

## How It Fits Together

```mermaid
flowchart LR
    A[Program runs] --> B[Writes memory to disk]
    B --> C[Program stops]
    C -.->|later| D[Program starts again]
    D --> E[Reads memory from disk]
    E --> F["Picks up where it left off"]
```

## Hands-On

```python
# %%
import json
from pathlib import Path

MEMORY_FILE = Path("long_term_memory.json")

def load_memories() -> list[dict]:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []

def save_memory(fact: str):
    memories = load_memories()
    memories.append({"fact": fact})
    MEMORY_FILE.write_text(json.dumps(memories, indent=2))

# %%
save_memory("Divesh is building a Udemy course on Agentic AI.")
save_memory("Divesh prefers Command Prompt over PowerShell.")

# %%
# Simulate a "restart" — load fresh from disk, not from a variable still in memory
print(load_memories())
```

## Common Pitfalls

- Using a local file as a real production memory store — fine for teaching the concept, but it doesn't scale, isn't safe for concurrent access, and isn't available to a service running on Cloud Run (Module 15). Topics 5-6 fix this properly.
- Forgetting the read-modify-write pattern can lose data if two processes write at the same time — a real database (topics 5-6) handles this for you; a JSON file does not.
- Storing *everything* long-term "just in case" — long-term storage should hold facts worth keeping, not the entire raw conversation (that's what short-term + summarization patterns are for, covered more in later modules).

## Quick Recap

1. What's the one property long-term memory adds that short-term memory doesn't have?
2. Why isn't a local JSON file a real production solution?
3. What problem does "read-modify-write" describe, and why does it matter?
