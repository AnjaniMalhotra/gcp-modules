# %% [markdown]
# # Topic 8 — Conversation Memory (Capstone)
# Wraps topics 4, 5, and 7 into one clean class an agent could actually call.
# Requires the Redis SSH tunnel from topic 4 to still be open.

# %%
import redis
from google.cloud.firestore_v1 import ArrayUnion
from setup import firestore_client

class ConversationMemory:
    def __init__(self, user_id: str, redis_host="localhost", redis_port=6379):
        self.user_id = user_id
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.firestore_doc = firestore_client.collection("long_term_memory").document(user_id)
        self.session_key = f"session:{user_id}:turns"

    def remember_turn(self, role: str, content: str):
        self.redis.rpush(self.session_key, f"{role}: {content}")
        self.redis.expire(self.session_key, 3600)

    def remember_fact(self, fact: str):
        self.firestore_doc.set({"facts": ArrayUnion([fact])}, merge=True)

    def recall(self) -> str:
        turns = self.redis.lrange(self.session_key, 0, -1)
        doc = self.firestore_doc.get()
        facts = doc.to_dict().get("facts", []) if doc.exists else []
        return (
            "Recent session:\n" + "\n".join(turns) +
            "\n\nKnown facts:\n" + "\n".join(facts)
        )

# %%
memory = ConversationMemory(user_id="user_divesh")
memory.remember_turn("user", "I'm recording Module 9 right now.")
memory.remember_fact("Currently recording the Memory Systems module")

# %%
print(memory.recall())

# %%
# This is what an agent would actually do: fetch context, then call Gemini with it
context = memory.recall()
print("\n--- This is what would get passed into a Gemini prompt ---\n")
print(context)
