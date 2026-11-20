"""M2 demo server: expose fixed teaching tools over MCP stdio.

M2_05_mcp_client_agent.py starts this server as a child process automatically.
Run this file by itself only when connecting an MCP inspector directly.
The server prints no regular output to stdout because stdout carries MCP messages.
"""

from mcp.server.mcpserver import MCPServer


# In MCP SDK v2, FastMCP was renamed to MCPServer. The v2 server retains the
# decorator-based tool pattern, but its import path and API have changed.
server = MCPServer("ai103-m2-demo")


@server.tool()
def lookup_course_topic(topic: str) -> str:
    """Look up a short description of a supported AI-103 topic."""
    # The dictionary makes this local server deterministic; no model/API is called here.
    topics = {
        "agent": "An AI agent combines a language model, instructions, and optional tools.",
        "mcp": "MCP lets an application discover and call tools exposed by a server.",
        "rag": "RAG retrieves relevant source material and gives it to a model as grounding context.",
    }
    normalized_topic = topic.strip().lower()
    return topics.get(normalized_topic, "No demo entry. Try agent, mcp, or rag.")


if __name__ == "__main__":
    # stdio runs this server as a child process controlled by an MCP client.
    server.run(transport="stdio")


# Test the complete example from the repository root:
#   python demos/m2/M2_05_mcp_client_agent.py
# M2_05 starts this server automatically; do not start a second copy in another
# terminal. Ask "Explain MCP in this course." Expected: a short answer based on the
# fixed lookup_course_topic result. The server itself uses stdio and prints no
# regular output; an MCP inspector can also launch this file to inspect its tool.
