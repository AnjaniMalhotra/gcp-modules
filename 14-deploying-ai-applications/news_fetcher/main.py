"""news-fetcher — a Cloud Function (2nd gen).

Fetches today's headlines from a free RSS feed, then calls news-summarizer
(Cloud Run) with an IAM-authenticated identity token - not an API key, not
a shared secret, a real per-request token scoped to that exact service URL.
"""

import os

import feedparser
import functions_framework
import google.auth.transport.requests
import google.oauth2.id_token
import requests

RSS_FEED_URL = os.environ.get(
    "RSS_FEED_URL",
    "https://news.google.com/rss/search?q=artificial+intelligence",
)
SUMMARIZER_URL = os.environ["SUMMARIZER_URL"]


def get_id_token(audience: str) -> str:
    """Get an identity token scoped to the target service's URL."""
    auth_req = google.auth.transport.requests.Request()
    return google.oauth2.id_token.fetch_id_token(auth_req, audience)


@functions_framework.http
def fetch_and_forward(request):
    feed = feedparser.parse(RSS_FEED_URL)
    headlines = [entry.title for entry in feed.entries[:10]]

    if not headlines:
        return {"error": "no headlines found in feed"}, 500

    token = get_id_token(SUMMARIZER_URL)
    response = requests.post(
        SUMMARIZER_URL,
        json={"headlines": headlines},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    return response.json(), response.status_code
