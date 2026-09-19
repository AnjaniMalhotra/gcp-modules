"""
Shared setup for every Python script in this module.

    from setup import genai_client, firestore_client, EMBEDDING_MODEL, ...

Run directly to sanity-check your environment:

    python setup.py

Config comes from .env (copy .env.example to .env first). This module is
self-contained — it does not import from another module, even
though the embeddings client below uses the same SDK taught there.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.cloud import firestore

load_dotenv()

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
REGION = os.environ["REGION"]
ZONE = os.environ["ZONE"]

REDIS_INSTANCE_NAME = os.environ["REDIS_INSTANCE_NAME"]
BASTION_VM_NAME = os.environ["BASTION_VM_NAME"]

CLOUD_SQL_INSTANCE_NAME = os.environ["CLOUD_SQL_INSTANCE_NAME"]
CLOUD_SQL_DB_NAME = os.environ["CLOUD_SQL_DB_NAME"]
CLOUD_SQL_USER = os.environ["CLOUD_SQL_USER"]
CLOUD_SQL_PASSWORD = os.environ["CLOUD_SQL_PASSWORD"]

EMBEDDING_MODEL = "text-embedding-005"
MODEL_FLASH = "gemini-2.5-flash"  # verify still current/GA - see code/03-vertex-ai-gemini/docs/02-gemini-models.md

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
firestore_client = firestore.Client(project=PROJECT_ID)

if __name__ == "__main__":
    print("Firestore project:", firestore_client.project)
    response = genai_client.models.generate_content(
        model=MODEL_FLASH,
        contents="Reply with exactly: setup OK",
    )
    print(response.text)
