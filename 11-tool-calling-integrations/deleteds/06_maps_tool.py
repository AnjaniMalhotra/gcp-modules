# %% [markdown]
# # Topic 6 — Maps API
# No OAuth needed here — just an API key (topic 7 explains why).

# %%
import googlemaps

from personal_assistant import config

gmaps = googlemaps.Client(key=config.MAPS_API_KEY)

# %%
geocode_result = gmaps.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
print(geocode_result[0]["formatted_address"])
print(geocode_result[0]["geometry"]["location"])

# %%
directions_result = gmaps.directions(
    "Golden Gate Bridge, San Francisco, CA",
    "Fisherman's Wharf, San Francisco, CA",
    mode="walking",
)
print(directions_result[0]["legs"][0]["duration"]["text"])
