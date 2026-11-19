"""M1 demo: First Responses API call.

Run from the project root: python demos/m1/M1_01_first_response.py
Sends one fixed teaching prompt and prints the model response.
Related slides: 19-23. SDK: the official OpenAI Python SDK, pointed at Foundry.
"""

# Import the shared setup helper so endpoint and secret handling is explained once.
from common import foundry_client


def main() -> None:
    # Create an OpenAI SDK client configured for the Foundry OpenAI-compatible URL.
    client, model = foundry_client()

    # responses.create sends one request to the model deployment selected above.
    response = client.responses.create(
        model=model,  # Foundry deployment name, not necessarily the base model name.
        input="What is the capital of France?",  # The user's prompt for this turn.
    )

    # output_text is the SDK convenience property for readable generated text.
    print(f"Answer: {response.output_text}")


if __name__ == "__main__":
    # This guard lets the file be imported without automatically making an API call.
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_01.
# Before running: deploy a Responses-compatible model in Foundry and configure .env.
# Command from project root: python demos/m1/M1_01_first_response.py

# Sample input and expected output for classroom demonstration:
# Showcase input (already in the code): What is the capital of France?
# Example expected output: Answer: Paris. Exact wording may vary by model.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_01_first_response.py
# This script sends the example prompt shown in main() to the configured deployment.
