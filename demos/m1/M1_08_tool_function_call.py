"""M1 demo: Local function calling.

Run from the project root: python demos/m1/M1_08_tool_function_call.py
Shows the model requesting a local function and the app returning its result.
Related slides: 28, 32, 36. Function tools run in your app, unlike hosted tools.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from common import foundry_client


def get_demo_time() -> str:
    """A deliberately small local function that reports the configured demo zone."""
    # This function executes on the learner's machine only after app-side validation.
    return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %Z")


def main() -> None:
    client, model = foundry_client()

    # JSON Schema describes the tool arguments so the model can construct valid input.
    tools = [
        {
            "type": "function",
            "name": "get_demo_time",
            "description": "Get the current demo time in the Asia/Kolkata time zone.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    ]
    response = client.responses.create(
        model=model,
        instructions="Use get_demo_time when asked for the current demo time.",
        input="What time is it in the demo time zone?",
        tools=tools,
    )

    # Retain the model's tool-call item in the next request's input history.
    follow_up_input = list(response.output)
    function_called = False
    for item in response.output:
        if item.type == "function_call" and item.name == "get_demo_time":
            # Validate the requested name before dispatching to application code.
            # For consequential tools, also validate arguments and require user approval.
            result = get_demo_time()
            follow_up_input.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result,
                }
            )
            function_called = True

    if not function_called:
        # The model may choose not to call a tool; show its normal answer instead.
        print(response.output_text)
        return

    # Send the function result back using the matching call_id; the model can now respond.
    final_response = client.responses.create(
        model=model,
        instructions="Answer naturally using the function output.",
        input=follow_up_input,
        tools=tools,
    )
    print(final_response.output_text)


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_08.
# Before running: configure a Responses deployment; get_demo_time runs in this app.
# Command from the project root: python demos/m1/M1_08_tool_function_call.py

# Sample input and expected output for classroom demonstration:
# Showcase input (already in the code): What time is it in the demo time zone?
# Example expected output: current Asia/Kolkata time in YYYY-MM-DD HH:MM:SS IST format; the time changes each run.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_08_tool_function_call.py
# Fixed prompt asks for the demo time; the function executes locally only after a model tool call.
