"""Command-line demo of the Personal Assistant Agent.

Requires: 03_google_apis_oauth_setup.py already run once (token.json
exists) and .env filled in with real values (no dummy placeholders left).
No infra to provision for this module — just OAuth + an API key.

Run with:  python main.py
"""

from personal_assistant.config import TEST_EMAIL_ADDRESS
from personal_assistant.pipeline import ask, build_assistant


def main():
    print("Building the Personal Assistant Agent...")
    agent = build_assistant()
    print("Assistant ready!\n")

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


if __name__ == "__main__":
    main()
