# %% [markdown]
# # Topic 5 — Firestore
# No provisioning script needed - Firestore is serverless and has a genuine
# free tier at this scale.

# %%
from setup import firestore_client
from google.cloud.firestore_v1 import ArrayUnion

memories_ref = firestore_client.collection("long_term_memory")

# %%
user_doc = memories_ref.document("user_divesh")
user_doc.set({
    "facts": ["Building a Udemy course on Agentic AI", "Prefers Command Prompt"],
}, merge=True)

# %%
snapshot = user_doc.get()
print(snapshot.to_dict())

# %%
# Add one more fact without overwriting the existing ones
user_doc.update({
    "facts": ArrayUnion(["Also likes teaching with Mermaid diagrams"]),
})
print(user_doc.get().to_dict())
