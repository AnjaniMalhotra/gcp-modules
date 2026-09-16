# 2. REST APIs

## What Is It? (Plain English)

A REST API is a standard way for one program to ask another program to do something over the internet — send a request to a URL, get a response back, usually as JSON. Every integration in this module (Gmail, Calendar, Maps) is, underneath, a REST API — Google just gives you a Python library so you don't write raw HTTP requests by hand.

## Why It Matters for AI Engineers

Not every service you'll want to connect an agent to will have a nice Python SDK. Sometimes it's just a REST endpoint and a piece of documentation. Knowing the raw pattern — build a request, send it, parse the response — means you can wire up *any* API as a tool, not just the ones Google conveniently wrapped for you.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Endpoint** | The specific URL you send a request to |
| **HTTP Method** | GET (fetch data), POST (send/create data), etc. |
| **Headers** | Extra metadata on a request — often where auth credentials go |
| **Request Body** | The data you send, usually JSON, on POST/PUT requests |
| **Response** | What comes back — a status code plus (usually) a JSON body |

## How It Fits Together

```mermaid
flowchart LR
    A["Your tool function"] --> B["Build request<br/>(URL + headers + body)"]
    B --> C["requests.post/get"]
    C --> D["External API"]
    D --> E["JSON response"]
    E --> F["Parse + return to the model"]
```

## Hands-On

```python
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
```

This is the exact same shape every Google API call in this module will follow — just with authentication added on top (starting topic 3).

## Common Pitfalls

- Not calling `raise_for_status()` (or checking the status code) — a failed request can silently return an error body that your code tries to parse as if it succeeded.
- Forgetting a timeout — a hung external API can hang your entire agent with it.
- Not handling the case where the API returns something unexpected — always wrap external calls defensively when they'll be used by an agent making autonomous decisions.

## Quick Recap

1. What are the four basic pieces of a REST API call?
2. Why does every Google API in this module still count as "a REST API"?
3. Why should a tool function always set a timeout on external requests?
