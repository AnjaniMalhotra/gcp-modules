# 5. Firestore

## What Is It? (Plain English)

Firestore is Google Cloud's flexible, serverless NoSQL document database. "Document" means data is stored as JSON-like objects, not rigid rows and columns — a natural fit for memory records that vary in shape from user to user.

## Why It Matters for AI Engineers

Unlike Redis and Cloud SQL, Firestore needs **no provisioning step, no bastion, and has a genuinely free tier** — 1 GiB storage and 50,000 reads a day, forever. For long-term memory that doesn't need Redis's raw speed, Firestore is usually the simplest correct choice.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Document** | One record, stored as a JSON-like object (fields + values) |
| **Collection** | A group of documents, roughly like a folder |
| **Document ID** | The unique key identifying one document within a collection (e.g., a user ID) |
| **Merge Write** | Updating specific fields on a document without overwriting the whole thing |

## How It Fits Together

```mermaid
flowchart LR
    A["Collection: conversation_memory"] --> B["Document: user_123"]
    A --> C["Document: user_456"]
    B --> D["{ facts: [...], last_seen: ... }"]
```

## Hands-On

```python
# %%
from setup import firestore_client

memories_ref = firestore_client.collection("long_term_memory")

# %%
# Write a memory for a specific user
user_doc = memories_ref.document("user_divesh")
user_doc.set({
    "facts": ["Building a Udemy course on Agentic AI", "Prefers Command Prompt"],
}, merge=True)

# %%
# Read it back
snapshot = user_doc.get()
print(snapshot.to_dict())

# %%
# Add one more fact without overwriting the existing ones
from google.cloud.firestore_v1 import ArrayUnion

user_doc.update({
    "facts": ArrayUnion(["Also likes teaching with Mermaid diagrams"]),
})
print(user_doc.get().to_dict())
```

## Common Pitfalls

- Using `.set()` without `merge=True` when you only meant to update part of a document — it overwrites the whole document by default.
- Modeling Firestore like a relational database (heavy cross-document joins) — it's not built for that; Cloud SQL (topic 6) is the right tool when your data is genuinely relational.
- Not indexing fields you'll query on frequently — Firestore needs an index for most non-trivial queries, and it'll tell you exactly which one to create if you're missing it.

## Quick Recap

1. What does "document" mean in the context of Firestore?
2. Why doesn't this topic need a provisioning script like Redis or Cloud SQL do?
3. What does `merge=True` change about a `.set()` call?
