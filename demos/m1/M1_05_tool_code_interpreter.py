"""M1 demo: Hosted Code Interpreter.

Run from the project root: python demos/m1/M1_05_tool_code_interpreter.py
Asks a hosted tool to perform a calculation; the code does not execute in local Python.
Related slides: 28-29, 33. Requires a deployment/API that supports this hosted tool.
"""

from common import foundry_client


def main() -> None:
    client, model = foundry_client()

    # The Responses API tools parameter advertises a hosted Python sandbox.
    response = client.responses.create(
        model=model,
        instructions="Use the Python tool for calculations, then explain the result.",
        input="A room is 10 meters by 6 meters. What is its area in square feet?",
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    )

    # Print the model's user-facing answer; raw tool events are in response.output.
    print(response.output_text)


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_05.
# Before running: verify the deployment/region supports Code Interpreter and confirm billing.
# Command from the project root: python demos/m1/M1_05_tool_code_interpreter.py

# Sample input and expected output for classroom demonstration:
# Showcase input (already in the code): A room is 8.5 meters by 6 meters. What is its area in square feet?
# Example expected output: approximately 548.96 square feet (51 square meters converted); wording may vary.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_05_tool_code_interpreter.py
# This script sends the example prompt shown in main() to the configured deployment.
