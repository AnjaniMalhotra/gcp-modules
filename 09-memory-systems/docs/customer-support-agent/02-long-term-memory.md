# 2. Long-Term Memory — Remembering a Returning Customer

## What Is It? (Plain English)

Long-term memory is anything SupportBot writes down that survives past the current chat — so when the same customer comes back next week, the bot isn't starting from zero.

## Why It Matters for AI Engineers

A support agent that asks "what plan are you on?" every single time a customer returns is a worse experience than a human agent who glances at a CRM first. Long-term memory is what makes an AI agent feel like it actually knows the customer.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Durability** | Survives the process restarting — the defining property this topic adds |
| **Fact Worth Keeping** | Not everything from a chat belongs here — only what matters beyond this one conversation |
| **Promotion** | The deliberate act of deciding something from short-term memory should become long-term |

## How It Fits Together

```mermaid
flowchart LR
    A["Chat: 'I'm on the Enterprise plan,<br/>had a billing issue last month'"] --> B{Worth keeping?}
    B -->|Yes| C["Written to durable storage"]
    C -.->|next week, new chat| D["SupportBot already knows"]
```

## Hands-On

See `customer_support_agent/02_long_term_memory.ipynb` — a local file stands in for durable storage here; topic 5 (Firestore) formalizes this properly.

```python
import json
from pathlib import Path

MEMORY_FILE = Path("support_customer_facts.json")

def remember_fact(customer_id: str, fact: str):
    facts = json.loads(MEMORY_FILE.read_text()) if MEMORY_FILE.exists() else {}
    facts.setdefault(customer_id, []).append(fact)
    MEMORY_FILE.write_text(json.dumps(facts, indent=2))

remember_fact("cust_042", "On the Enterprise plan")
remember_fact("cust_042", "Had a billing issue resolved on Jan 5")

# Simulate the customer returning next week — read fresh from disk
facts = json.loads(MEMORY_FILE.read_text())
print(facts["cust_042"])
```

## Common Pitfalls

- Writing every single message to long-term storage "just in case" — bloats storage and dilutes what actually matters; be deliberate about what gets promoted.
- Using a local file as the real production answer — fine for teaching the concept, not for a real multi-instance support system (topic 5 fixes this).
- Forgetting long-term memory needs a customer identifier to actually be useful — "facts" with no owner are useless the moment you have more than one customer.

## Quick Recap

1. What's the one property long-term memory adds over short-term memory?
2. Why shouldn't SupportBot save every message to long-term storage?
3. What's missing from this local-file version that a real production system would need?
