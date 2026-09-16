"""Shared setup for every notebook in this module.

    from setup import genai_client, MODEL_FLASH, PROJECT_ID, ...

Run directly to sanity-check your environment:

    python 00_setup.py

Config comes from .env (copy .env.example to .env first). Self-contained —
no imports from code/09-memory-systems/, even though topics 3-4 reuse
patterns taught there.
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
REGION = os.environ["REGION"]
ZONE = os.environ["ZONE"]

GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]

CLOUD_SQL_INSTANCE_NAME = os.environ["CLOUD_SQL_INSTANCE_NAME"]
CLOUD_SQL_DB_NAME = os.environ["CLOUD_SQL_DB_NAME"]
CLOUD_SQL_USER = os.environ["CLOUD_SQL_USER"]
CLOUD_SQL_PASSWORD = os.environ["CLOUD_SQL_PASSWORD"]

REDIS_INSTANCE_NAME = os.environ["REDIS_INSTANCE_NAME"]
BASTION_VM_NAME = os.environ["BASTION_VM_NAME"]

MODEL_FLASH = "gemini-2.5-flash"  # verify still current/GA - see code/03-vertex-ai-gemini/docs/02-gemini-models.md

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

if __name__ == "__main__":
    response = genai_client.models.generate_content(
        model=MODEL_FLASH,
        contents="Reply with exactly: setup OK",
    )
    print(response.text)
