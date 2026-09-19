# %% [markdown]
# # Topic 3 — Google APIs: One-Time OAuth Setup
#
# READ docs/03-google-apis.md FIRST — it has
# the full step-by-step Google Cloud Console walkthrough (enabling APIs,
# configuring the consent screen, creating the OAuth Client ID) that has to
# happen before this script will work.
#
# Run this ONCE. It opens your browser, asks you to pick your Google
# account and click "Allow," then saves token.json so every future run
# (in this script or anywhere else in this module) skips the browser
# entirely.
#
# Requires client_secret.json to already be in this folder (downloaded
# from the Console — see the doc above).

# %%
from personal_assistant import config
from personal_assistant.auth import get_credentials

creds = get_credentials()
print(f"Success! {config.TOKEN_FILE} created/refreshed.")
print("Scopes granted:", creds.scopes)
