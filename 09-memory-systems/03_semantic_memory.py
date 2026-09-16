# %% [markdown]
# # Topic 3 — Semantic Memory
# Store memories as embeddings, retrieve by MEANING instead of exact text
# match. Self-contained — does not import from code/03-vertex-ai-gemini/,
# even though it's the same embeddings API taught there.

# %%
import numpy as np
from setup import genai_client, EMBEDDING_MODEL

def embed(text: str) -> np.ndarray:
    result = genai_client.models.embed_content(model=EMBEDDING_MODEL, contents=[text])
    return np.array(result.embeddings[0].values)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# %%
memories = [
    "The user's favorite color is blue.",
    "The user lives in Mumbai.",
    "The user is building a Udemy course on cloud AI.",
]
memory_vectors = [embed(m) for m in memories]

# %%
def recall(query: str, top_k: int = 1):
    query_vector = embed(query)
    scored = [(cosine_similarity(query_vector, v), m) for v, m in zip(memory_vectors, memories)]
    scored.sort(reverse=True)
    return scored[:top_k]

print(recall("Where does the user stay?"))
