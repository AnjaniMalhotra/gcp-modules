# %% [markdown]
# # Topic 7 — Authentication: All Three Patterns, Side by Side

# %%
# 1. API key — Maps (no OAuth, doesn't touch personal data)
import googlemaps
from personal_assistant import config

gmaps = googlemaps.Client(key=config.MAPS_API_KEY)
print("API key auth:", gmaps.geocode("Mumbai, India")[0]["formatted_address"])

# %%
# 2. OAuth — Gmail (acting as the specific human who clicked "Allow" in topic 3)
from googleapiclient.discovery import build
from personal_assistant.auth import get_credentials

creds = get_credentials()
gmail_service = build("gmail", "v1", credentials=creds)
profile = gmail_service.users().getProfile(userId="me").execute()
print("OAuth auth: acting as", profile["emailAddress"])

# %%
# 3. Service account / ADC — Vertex AI Gemini (acting as itself, from Module 3)
from google import genai

client = genai.Client(vertexai=True, project=config.PROJECT_ID, location=config.LOCATION)
print("Service account / ADC auth: Vertex AI client ready for project", config.PROJECT_ID)

# %% [markdown]
# ## Now the combined demo
# See main.py for the full Personal Assistant Agent, using all three
# patterns together under the hood.
