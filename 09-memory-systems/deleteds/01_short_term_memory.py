# %% [markdown]
# # Topic 1 — Short-Term Memory
# The simplest possible memory: a Python list, alive only as long as the
# process runs. No cloud, no persistence — that's the whole point of
# "short-term."

# %%
class ShortTermMemory:
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.turns: list[dict] = []

    def add(self, role: str, content: str):
        self.turns.append({"role": role, "content": content})
        self.turns = self.turns[-self.max_turns:]  # sliding window

    def as_context(self) -> str:
        return "\n".join(f"{t['role']}: {t['content']}" for t in self.turns)

# %%
memory = ShortTermMemory(max_turns=3)
memory.add("user", "My name is Divesh.")
memory.add("assistant", "Nice to meet you, Divesh!")
memory.add("user", "What's my name?")
print(memory.as_context())

# %%
# Push past the window — watch the oldest turn silently drop
memory.add("assistant", "Your name is Divesh.")
memory.add("user", "What's 2+2?")
print(memory.as_context())  # "My name is Divesh" is now gone
