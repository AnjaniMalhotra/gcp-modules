"""Wires everything together — the single entry point main.py calls."""

from personal_assistant import config
from personal_assistant.agent import create_personal_assistant_agent
from personal_assistant.llm import get_llm


def build_assistant():
    config.check_config()
    llm = get_llm()
    return create_personal_assistant_agent(llm)


def chat_turn(agent, messages: list, question: str) -> tuple[str, list]:
    """One turn of a conversation. Returns (answer, the updated message history)."""
    response = agent.invoke({"messages": messages + [{"role": "user", "content": question}]})
    # .content can be a list of content blocks (Gemini thought signatures), .text is always the plain string
    return str(response["messages"][-1].text), response["messages"]


def ask(agent, question: str) -> str:
    return chat_turn(agent, [], question)[0]
