# %% [markdown]
# # Topic 7 — Hybrid Memory
# Combines topic 4 (Redis) and topic 5 (Firestore). Requires the Redis SSH
# tunnel from topic 4 to still be open in its own window.

# %%
import redis
from google.cloud.firestore_v1 import ArrayUnion
from setup import firestore_client

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
memories_ref = firestore_client.collection("long_term_memory")

# %%
def remember_turn(user_id: str, role: str, content: str):
    # short-term: session cache, expires in 1 hour
    key = f"session:{user_id}:turns"
    r.rpush(key, f"{role}: {content}")
    r.expire(key, 3600)

def remember_fact(user_id: str, fact: str):
    # long-term: durable, no expiry
    memories_ref.document(user_id).set({"facts": ArrayUnion([fact])}, merge=True)

# %%
remember_turn("user_divesh", "user", "Remind me I prefer Command Prompt.")
remember_fact("user_divesh", "Prefers Command Prompt over PowerShell")

# %%
def recall_context(user_id: str) -> str:
    session_turns = r.lrange(f"session:{user_id}:turns", 0, -1)
    facts_doc = memories_ref.document(user_id).get()
    facts = facts_doc.to_dict().get("facts", []) if facts_doc.exists else []

    return (
        "Recent session:\n" + "\n".join(session_turns) +
        "\n\nKnown facts:\n" + "\n".join(facts)
    )

print(recall_context("user_divesh"))
