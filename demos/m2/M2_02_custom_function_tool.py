"""M2 demo: let an agent choose a custom Python function tool.

Run from the project root: python demos/m2/M2_02_custom_function_tool.py
The tool returns fictional sample data for Seattle and Denver; it does not call
a weather API. Type quit to finish.
"""

import asyncio
from typing import Annotated

from agent_framework import tool
from pydantic import Field

from common import foundry_chat_client


@tool(approval_mode="never_require")
def get_demo_weather(
    city: Annotated[str, Field(description="A supported demo city: Seattle or Denver")],
) -> str:
    """Return fixed fictional weather data. This is a read-only teaching tool."""
    sample_weather = {
        "seattle": "light rain, 12 C",
        "denver": "sunny, 18 C",
    }
    weather = sample_weather.get(city.strip().lower())
    if weather is None:
        return f"No demo data for {city}. Supported cities are Seattle and Denver."
    return f"Demo weather for {city.title()}: {weather}. This is sample data, not a live forecast."


async def main() -> None:
    client, credential = foundry_chat_client()
    try:
        agent = client.as_agent(
            name="demo-weather-agent",
            instructions=(
                "Answer weather questions using get_demo_weather. "
                "Always say its results are fixed sample data, not a live forecast."
            ),
            tools=[get_demo_weather],
        )

        print("Demo Weather Agent is ready. Ask about a city, or type 'quit'.")
        while True:
            question = input("\nYou: ").strip()
            if question.lower() in {"quit", "exit"}:
                print("Agent: Goodbye!")
                break
            if not question:
                print("Enter a question, or type 'quit' to leave.")
                continue

            # The framework gives the model this tool's name, description, and schema.
            # If it selects the tool, Python executes it and the framework returns the result.
            result = await agent.run(question)
            print(f"Agent: {result.text}")
    finally:
        await client.close()
        credential.close()


if __name__ == "__main__":
    asyncio.run(main())


# How to run from the project root in the VS Code terminal:
#   python demos/m2/M2_02_custom_function_tool.py
# Try: What is the demo weather in Seattle? Then ask about an unsupported city.
# Workflow: prompt -> model selects tool -> local function returns data -> model answers.
# approval_mode="never_require" is limited to this harmless read-only sample lookup.
# Expected: the agent reports Seattle's fixed "light rain, 12 C" sample data or
# explains that another city has no sample entry. It never calls a live weather API.
