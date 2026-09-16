"""Gmail as an agent tool — wraps topic 4's read/send logic as a @tool."""

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from langchain.tools import tool

from personal_assistant.auth import get_credentials


def _get_gmail_service():
    return build("gmail", "v1", credentials=get_credentials())


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. Use this to notify someone about a scheduled meeting
    or any other information the user asks you to send."""
    service = _get_gmail_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": encoded}).execute()
    return f"Email sent to {to} with subject '{subject}'."


@tool
def read_recent_emails(max_results: int = 3) -> str:
    """Read the most recent emails in the user's inbox."""
    service = _get_gmail_service()
    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    snippets = []
    for msg in results.get("messages", []):
        detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
        snippets.append(detail["snippet"])
    return "\n\n".join(snippets) if snippets else "No recent emails found."
