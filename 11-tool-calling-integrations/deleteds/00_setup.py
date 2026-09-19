"""Shared setup for every script in this module.

    from setup import llm_client, PROJECT_ID, ...

Run directly to sanity-check your environment:

    python 00_setup.py

Config comes from .env (copy .env.example to .env first, then replace every
DUMMY VALUE in it with a real one). This module is self-contained — no
imports from code/10-rag-engineering/.
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
MAPS_API_KEY = os.environ["MAPS_API_KEY"]
TEST_EMAIL_ADDRESS = os.environ["TEST_EMAIL_ADDRESS"]

MODEL_FLASH = "gemini-2.5-flash"  # verify still current/GA - see code/03-vertex-ai-gemini/docs/02-gemini-models.md

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

if __name__ == "__main__":
    response = genai_client.models.generate_content(
        model=MODEL_FLASH,
        contents="Reply with exactly: setup OK",
    )
    print(response.text)
    if MAPS_API_KEY == "your-maps-api-key-here":
        print("WARNING: MAPS_API_KEY is still the dummy placeholder value — replace it in .env")
