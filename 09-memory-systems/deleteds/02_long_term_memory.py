# %% [markdown]
# # Topic 2 — Long-Term Memory
# Same idea as short-term, but written somewhere that survives the process
# ending. Here: a local JSON file — the simplest possible "long-term" store,
# before we reach for a real cloud database in topics 5-6.

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
