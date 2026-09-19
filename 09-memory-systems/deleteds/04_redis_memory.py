# %% [markdown]
# # Topic 4 — Redis
# Requires: 04a_provision_redis_and_bastion.bat already run, AND the SSH
# tunnel from a second Command Prompt window still open (see that script's
# printed instructions). This script talks to localhost:6379, which the
# tunnel transparently forwards to the real Memorystore instance.

# %%
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# %%
r.set("session:demo-user:last_message", "Hello from Redis!")
r.expire("session:demo-user:last_message", 3600)  # auto-deletes after 1 hour

print(r.get("session:demo-user:last_message"))
print("TTL remaining (seconds):", r.ttl("session:demo-user:last_message"))

# %%
# A list-shaped key, like you'd use for a running session transcript
r.rpush("session:demo-user:turns", "user: Hi there", "assistant: Hello!")
r.expire("session:demo-user:turns", 3600)
print(r.lrange("session:demo-user:turns", 0, -1))
