"""Command-line entry point for the Personal Assistant Agent.

Requires: 03_google_apis_oauth_setup.py already run once (the token file
exists) and .env filled in with real values (no dummy placeholders left).
No infra to provision for this module — just OAuth + an API key.

    python main.py                       run the 3-question demo (books an event, sends an email)
    python main.py --chat                talk to it; it remembers the conversation
    python main.py "What are my plans?"  ask one question and exit

The assistant really can send email and create events when you ask it to.
"""

import sys

from personal_assistant.config import TEST_EMAIL_ADDRESS
from personal_assistant.pipeline import ask, build_assistant, chat_turn


def run_demo(agent):
    demo_questions = [
        "What's the address of the Golden Gate Bridge?",
        "Am I free in 2 hours?",
        (
            f"Check if I'm free 3 hours from now. If so, schedule a 30 minute "
            f"'Module 11 Demo Meeting', then email {TEST_EMAIL_ADDRESS} to let "
            f"them know it's booked."
        ),
    ]

    for question in demo_questions:
        print("=" * 60)
        print("QUESTION:", question)
        print("-" * 60)
        answer = ask(agent, question)
        print("ANSWER:", answer)
        print("=" * 60)
        print()


def run_chat(agent):
    print("Ask about your plans, email, or directions. Type 'quit' to stop.")
    print("Careful: it can really send email and create calendar events.\n")
    messages = []
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        answer, messages = chat_turn(agent, messages, question)
        print(f"Assistant: {answer}\n")


def main():
    args = sys.argv[1:]
    print("Building the Personal Assistant Agent...")
    agent = build_assistant()
    print("Assistant ready!\n")

    if args == ["--chat"]:
        run_chat(agent)
    elif args:
        print(ask(agent, " ".join(args)))
    else:
        run_demo(agent)


if __name__ == "__main__":
    main()
