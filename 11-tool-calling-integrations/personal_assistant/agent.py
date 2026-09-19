"""Build the agent that ties the LLM and all three tools together.

One agent, three tools, three different auth patterns underneath — the
agent itself doesn't need to know or care which is which.
"""

from datetime import datetime

from langchain.agents import create_agent

from personal_assistant import config
from personal_assistant.calendar_tool import check_availability, create_event, list_events
from personal_assistant.gmail_tool import read_recent_emails, send_email
from personal_assistant.maps_tool import get_address_details, get_directions


def create_personal_assistant_agent(llm):
    now = datetime.now().astimezone()
    system_prompt = (
        f"{config.SYSTEM_PROMPT} The current date and time is "
        f"{now:%A %d %B %Y, %H:%M} ({now.tzname()}, UTC{now:%z}). The calendar "
        "tools take times as hours from now, so work out how many hours from "
        "this moment the time the user asks about is."
    )
    tools = [
        check_availability,
        create_event,
        list_events,
        send_email,
        read_recent_emails,
        get_address_details,
        get_directions,
    ]
    return create_agent(model=llm, tools=tools, system_prompt=system_prompt)
