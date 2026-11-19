"""M1 demo: Chat Completions history.

Run from the project root: python demos/m1/M1_03_chat_completions_history.py
Interactive chat resends the app-managed messages list every turn.
Related slides: 21-24. The application resends the full messages list each turn.
"""

from common import foundry_client


def main() -> None:
    client, model = foundry_client()

    # Chat Completions uses a list of role/content messages as the conversation.
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer clearly and concisely.",
        }
    ]

    print("Type quit to end the conversation.")
    while True:
        user_text = input("\nYou: ").strip()
        if user_text.lower() == "quit":
            print("Assistant: Goodbye!")
            break
        if not user_text:
            print("Please enter a message.")
            continue

        # Add the new user turn; prior turns remain in the list for context.
        messages.append({"role": "user", "content": user_text})

        # chat.completions.create is the Chat Completions API method in the SDK.
        completion = client.chat.completions.create(model=model, messages=messages)

        # The first choice contains the assistant's generated message for this call.
        assistant_text = completion.choices[0].message.content or ""
        print(f"Assistant: {assistant_text}")

        # Append the assistant answer so it will be included in the next request.
        messages.append({"role": "assistant", "content": assistant_text})


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_03.
# Before running: choose a deployment that supports Chat Completions and configure .env.
# Command from the project root: python demos/m1/M1_03_chat_completions_history.py; type quit to exit.

# Sample input and expected output for classroom demonstration:
# Sample terminal inputs, one per prompt: When was Microsoft founded? | Who founded it? | quit
# Example output: April 4, 1975; then Bill Gates and Paul Allen. Exact wording may vary.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_03_chat_completions_history.py
# Enter messages; type quit to finish. The script resends its local messages list on every turn.
