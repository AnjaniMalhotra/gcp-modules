"""Shared setup for the SupportBot notebooks.

    from setup import genai_client, firestore_client, EMBEDDING_MODEL, MODEL_FLASH

Loads .env from the PARENT folder (09-memory-systems/.env) rather than
duplicating it — this scenario reuses the same project config and the same
provisioned Redis/Cloud SQL infrastructure as the original Module 9 topics,
just with different table/collection names so both can coexist.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.cloud import firestore

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
REGION = os.environ["REGION"]
ZONE = os.environ["ZONE"]

CLOUD_SQL_INSTANCE_NAME = os.environ["CLOUD_SQL_INSTANCE_NAME"]
CLOUD_SQL_DB_NAME = os.environ["CLOUD_SQL_DB_NAME"]
CLOUD_SQL_USER = os.environ["CLOUD_SQL_USER"]
CLOUD_SQL_PASSWORD = os.environ["CLOUD_SQL_PASSWORD"]

# The local end of the SSH tunnel to Memorystore (see ../commands.md). Change REDIS_PORT if
# something on your machine, like a local Redis, already owns 6379.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

EMBEDDING_MODEL = "text-embedding-005"
MODEL_FLASH = "gemini-2.5-flash"  # verify still current/GA - see code/03-vertex-ai-gemini/docs/02-gemini-models.md

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
firestore_client = firestore.Client(project=PROJECT_ID)

if __name__ == "__main__":
    print("Firestore project:", firestore_client.project)
    response = genai_client.models.generate_content(model=MODEL_FLASH, contents="Reply with exactly: setup OK")
    print(response.text)
