"""M1 demo: Responses conversation state.

Run from the project root: python demos/m1/M1_02_responses_conversation.py
Interactive chat links turns by passing previous_response_id.
Related slides: 21-23. State is carried by previous_response_id on each turn.
"""

from common import foundry_client


def main() -> None:
    # Prepare the client once; subsequent turns reuse the same HTTP client.
    client, model = foundry_client()

    # The first turn has no earlier response, so this starts a new conversation.
    previous_response_id = None
    instructions = "You are a helpful AI assistant that explains technology clearly."

    print("Type quit to end the conversation.")
    while True:
        # Read one user turn from the terminal and normalize surrounding whitespace.
        user_text = input("\nYou: ").strip()
        if user_text.lower() == "quit":
            print("Assistant: Goodbye!")
            break
        if not user_text:
            print("Please enter a message.")
            continue

        # The Responses API can keep state server-side by linking to the prior ID.
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=user_text,
            previous_response_id=previous_response_id,
        )
        print(f"Assistant: {response.output_text}")

        # Save the new response ID so the next turn has the conversation context.
        previous_response_id = response.id

        print(f"(Debug: previous_response_id={previous_response_id})")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_02.
# Before running: configure the Foundry endpoint, key, and deployment in .env.
# Command from the project root: python demos/m1/M1_02_responses_conversation.py; type quit to exit.

# Sample input and expected output for classroom demonstration:
# Sample terminal inputs, one per prompt: What is photosynthesis? | Explain it in one sentence for a 10-year-old. | quit
# Example output: first answer defines photosynthesis; follow-up explains it using that context; quit prints Assistant: Goodbye!.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_02_responses_conversation.py
# Enter messages; type quit to finish. Each turn sends previous_response_id for service-managed context.
