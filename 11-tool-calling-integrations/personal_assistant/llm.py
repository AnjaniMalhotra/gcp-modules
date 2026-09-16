"""Connect to the LLM — Vertex AI Gemini, same pattern as Module 10."""

from langchain_google_genai import ChatGoogleGenerativeAI

from personal_assistant import config


def get_llm():
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL_NAME,
        vertexai=True,
        project=config.PROJECT_ID,
        location=config.LOCATION,
        temperature=0,
    )
