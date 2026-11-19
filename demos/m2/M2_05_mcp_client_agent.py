"""M2 demo: let a Foundry-backed agent discover and use a local MCP tool.

Start M2_04_local_mcp_server.py in VS Code terminal 1, then run this in terminal 2:
    python demos/m2/M2_05_mcp_client_agent.py
Requires the standard Foundry .env settings, az login, and MCP/Agent Framework packages.
"""

import asyncio
import sys
from pathlib import Path

from agent_framework import Agent, MCPStdioTool

from common import foundry_chat_client

SERVER_FILE = Path(__file__).with_name("M2_04_local_mcp_server.py")


async def main() -> None:
    # MCPStdioTool launches the local server and discovers its registered tools.
    async with MCPStdioTool(
        name="course-topics",
        command=sys.executable,
        args=[str(SERVER_FILE)],
    ) as mcp_server:
        # The model sees tool descriptions and can decide when to ask the server.
        agent = foundry_chat_client().as_agent(
            name="mcp-course-agent",
            instructions=(
                "Use the course topic MCP lookup when useful. "
                "If a topic is unsupported, say no entry was found."
            ),
        )

        print("MCP Course Agent is ready. Ask about agent, MCP, or RAG; type 'quit' to end.")
        while True:
            question = input("\nYou: ").strip()
            if question.lower() in {"quit", "exit"}:
                print("Agent: Goodbye!")
                break
            if not question:
                print("Enter a question, or type 'quit' to leave.")
                continue

            # Passing mcp_server makes its discovered tools available for this run.
            # Framework handles call_tool and returns the result into agent context.
            result = await agent.run(question, tools=mcp_server)
            print(f"Agent: {result.text}")


if __name__ == "__main__":
    asyncio.run(main())


# Try: Explain MCP in this course. Then ask what RAG means or ask about an unknown topic.
# Workflow: user's message -> model chooses discovered MCP tool -> server returns
# result -> framework gives result to model -> agent writes its answer.
