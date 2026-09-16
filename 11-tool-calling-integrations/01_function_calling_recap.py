# %% [markdown]
# # Topic 1 — Function Calling (Recap)
# Nothing new here — same mechanism from Module 3, used for real in Module
# 10. This file exists just to prove it's still exactly the same idea
# before we point it at real external APIs.

# %%
from langchain.tools import tool

@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

print(add_numbers.name, "-", add_numbers.description)
print(add_numbers.invoke({"a": 2, "b": 3}))
