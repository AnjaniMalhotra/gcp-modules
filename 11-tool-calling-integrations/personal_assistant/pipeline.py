"""Wires everything together — the single entry point main.py calls."""

from personal_assistant import config
from personal_assistant.agent import create_personal_assistant_agent
from personal_assistant.llm import get_llm


def build_assistant():
    config.check_config()
    llm = get_llm()
    return create_personal_assistant_agent(llm)


def ask(agent, question: str) -> str:
    response = agent.invoke({"messages": [{"role": "user", "content": question}]})
    # .content can be a list of content blocks (Gemini thought signatures), .text is always the plain string
    return str(response["messages"][-1].text)
