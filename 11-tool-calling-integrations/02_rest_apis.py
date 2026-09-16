# %% [markdown]
# # Topic 2 — REST APIs
# The general pattern every Google API call in this module follows
# underneath: build a request, send it, parse the JSON response.

# %%
import requests
from langchain.tools import tool

@tool
def get_random_fact() -> str:
    """Fetch a random useless fact from a public API."""
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random", timeout=10)
    response.raise_for_status()
    return response.json()["text"]

# %%
print(get_random_fact.invoke({}))
