"""M2 demo: create an interactive Microsoft Agent Framework agent.

Run from the project root: python demos/m2/M2_01_first_agent.py
Prerequisites: install requirements.txt, set AZURE_AI_FOUNDRY_PROJECT_ENDPOINT
and AZURE_AI_FOUNDRY_MODEL in .env, run az login, and have project/model access.
Type quit to end the conversation.
"""

import asyncio

from common import foundry_chat_client


async def main() -> None:
    # A chat client connects the local Python app to the deployed Foundry model.
    client, credential = foundry_chat_client()
    try:
        # as_agent wraps the model client with a name and stable behavior instructions.
        agent = client.as_agent(
            name="python-tutor",
            instructions="You are a concise Python tutor. Give a short explanation and a tiny example.",
        )

        print("Python Tutor is ready. Ask a Python question, or type 'quit'.")
        while True:
            question = input("\nYou: ").strip()
            if question.lower() in {"quit", "exit"}:
                print("Tutor: Goodbye!")
                break
            if not question:
                print("Enter a question, or type 'quit' to leave.")
                continue

            # Each run sends the user turn to the agent and prints its response.
            # The simple example creates no persistent cloud agent resource.
            result = await agent.run(question)
            print(f"Tutor: {result.text}")
    finally:
        await client.close()
        credential.close()


if __name__ == "__main__":
    # Agent Framework calls are asynchronous; asyncio runs the async main function.
    asyncio.run(main())


# How to run from the project root in the VS Code terminal:
#   python demos/m2/M2_01_first_agent.py
# Sample interaction: What is a Python list? -> tutor explains and shows an example.
# Try a follow-up: How do I add an item? Then type quit.
# Workflow: input -> Agent (instructions + Foundry model) -> result.text -> terminal.
# Expected: two concise Python explanations that use prior-turn context, followed by
# "Tutor: Goodbye!" after quit. These are local Agent Framework objects, not a saved
# portal agent.
