# %% [markdown]
# # Topic 6 — Cloud SQL
# Requires: 06a_provision_cloud_sql.bat already run (kick it off back during
# topic 4 - it's slow). Unlike Redis, no bastion VM or tunnel needed - the
# Cloud SQL Python Connector handles a secure connection over the public
# internet on its own.

# %%
import sqlalchemy
from google.cloud.sql.connector import Connector
from setup import PROJECT_ID, REGION, CLOUD_SQL_INSTANCE_NAME, CLOUD_SQL_DB_NAME, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD

connector = Connector()

def getconn():
    return connector.connect(
        f"{PROJECT_ID}:{REGION}:{CLOUD_SQL_INSTANCE_NAME}",
        "pg8000",
        user=CLOUD_SQL_USER,
        password=CLOUD_SQL_PASSWORD,
        db=CLOUD_SQL_DB_NAME,
    )

engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

# %%
with engine.connect() as conn:
    conn.execute(sqlalchemy.text("""
        CREATE TABLE IF NOT EXISTS memories (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            fact TEXT NOT NULL
        )
    """))
    conn.commit()

# %%
with engine.connect() as conn:
    conn.execute(
        sqlalchemy.text("INSERT INTO memories (user_id, fact) VALUES (:user_id, :fact)"),
        {"user_id": "user_divesh", "fact": "Prefers Cloud SQL for structured memory"},
    )
    conn.commit()

    result = conn.execute(
        sqlalchemy.text("SELECT * FROM memories WHERE user_id = :uid"),
        {"uid": "user_divesh"},
    )
    for row in result:
        print(row)

# %%
connector.close()
