# bat-files/

The original Windows provisioning scripts for this module, kept unchanged for
reference. On macOS or Linux use the equivalent `gcloud` commands in
`../commands.md`, which are what was actually run.

| File | What it does |
|---|---|
| `00_setup_vars.bat` | Sets the shared variables (project, region, resource names, database password) |
| `04a_provision_redis_and_bastion.bat` | Creates Memorystore Redis and the bastion VM |
| `06a_provision_cloud_sql.bat` | Creates the Cloud SQL Postgres instance and its database |
| `99_cleanup.bat` | Deletes Cloud SQL, Redis and the bastion VM |

To use them on Windows: run `00_setup_vars.bat` first, **in the same Command
Prompt window** as the others, after changing its `PROJECT_ID` and
`CLOUD_SQL_PASSWORD` to real values.

Keep their Windows (CRLF) line endings. Converting them to Unix endings breaks
them in Command Prompt.
