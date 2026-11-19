"""M1 demo: Hosted web search.

Run from the project root: python demos/m1/M1_06_tool_web_search.py
Asks a supported deployment to find current information using its hosted search tool.
Related slides: 28, 30, 34. Requires a deployment and region that support web_search.
"""

from common import foundry_client


def main() -> None:
    client, model = foundry_client()

    # web_search allows the hosted model workflow to retrieve current web sources.
    response = client.responses.create(
        model=model,
        instructions=(
            "Use web search for current information. Summarize in your own words "
            "and include source links when available."
        ),
        input="Find two recent Microsoft AI announcements and summarize each.",
        tools=[{"type": "web_search"}],
    )
    print(response.output_text)


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_06.
# Before running: verify web_search support and project/network policy in Foundry.
# Command from the project root: python demos/m1/M1_06_tool_web_search.py

# Sample input and expected output for classroom demonstration:
# Showcase input (already in the code): Find two recent Microsoft AI announcements and summarize each.
# Expected behavior: current summary and source links. Search availability and results change; verify links during class.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_06_tool_web_search.py
# This script sends the example prompt shown in main() to the configured deployment.
