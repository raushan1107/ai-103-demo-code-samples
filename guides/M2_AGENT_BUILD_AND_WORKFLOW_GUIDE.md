# Module 2: Build and understand agents in Python

This guide explains what the M2 Python demos create, how agent calls work, how to run each file in VS Code, and how the pieces fit together. Start with the simple client-side agent, then move to custom tools and service-managed prompt agents. The examples are teaching programs: they make the parts visible and do not deploy a production application.

## The short version: what is an agent?

An **agent** is an application pattern built around a language model. For these demos, it consists of:

1. **A model connection** — tells Python which Microsoft Foundry project and deployed model to contact.
2. **Instructions** — describe the agent's role and how it should respond.
3. **Optional tools** — Python functions or MCP tools the model may request when they help answer a question.
4. **A run loop** — sends user input, handles any tool request, and displays the response.
5. **Conversation state** — keeps relevant earlier turns available for follow-up questions.

The model does not directly execute Python code. It can request a named tool with structured arguments. The application/framework decides whether that request is permitted, runs the function or forwards it to an MCP server, then returns the result to the model. The model writes the final answer.

## Two meanings of “create an agent”

This distinction is often the confusing part. The demos use two patterns:

| Pattern | What gets created | Where it lives | Main files |
| --- | --- | --- | --- |
| Agent Framework client agent | A Python agent object assembled from a client, instructions, and optional tools | In the running Python process; no persistent agent resource is created by these examples | M2_01, M2_02, M2_05, M2_07 |
| Foundry prompt agent | A named, versioned agent definition with a model, instructions, and tool declarations | In the Microsoft Foundry project | M2_03 and M2_06 create temporary versions; M2_08 connects to an existing one |

“Create” in M2_01 means construct an in-memory Python object. “Create” in M2_03/M2_06 means ask the Foundry service to save a versioned resource. M2_08 creates neither: it uses a resource already created in the portal.

## Prepare the workspace

Open `R:\Demos\AI-103` as the VS Code workspace. In the integrated terminal, activate the project environment and install the packages:

```powershell
python -m pip install -r requirements.txt
az login
```

The M2 files authenticate with the signed-in Azure CLI identity. Add the project endpoint and model **deployment name** to the project-root `.env` file:

```text
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_AI_FOUNDRY_MODEL=<deployed-model-name>
```

Find the project endpoint in the Foundry project details and the exact deployment name under deployed models. The identity used by `az login` must have permission to use the project and model. **Do not copy the M1 `AZURE_AI_FOUNDRY_ENDPOINT` into the M2 project endpoint setting:** M1 uses an OpenAI-compatible endpoint and API key; M2 uses a project endpoint and Entra ID. They are separate endpoint and authentication configurations, even when they refer to the same Foundry resource.

The shared helper `demos/m2/common.py` loads `.env`, checks required settings, and creates `FoundryChatClient`. Each demo keeps its central setup and request in the topic file so the teaching flow stays visible.

## The workflow to keep in mind

```text
user input
   ↓
Python application sends input + instructions + available tool descriptions
   ↓
model responds with text OR requests a tool and supplies arguments
   ↓
framework/application runs the local function or calls an MCP server
   ↓
tool result is returned to the model
   ↓
model writes a user-facing response
```

Without tools, the tool-request and tool-result steps are skipped. With a sequential workflow, multiple agents run one after another and pass context forward.

## Run the demos in order

Run every command from the workspace root in the VS Code terminal. Interactive examples accept repeated turns; one-shot examples say so in their section.

### 1. M2_01 — first Agent Framework agent

```powershell
python demos/m2/M2_01_first_agent.py
```

The file calls `foundry_chat_client()` to connect to a deployed Foundry model. `as_agent(...)` supplies a name and instructions. Each `agent.run(question)` sends one user turn, and `result.text` is printed. This local object is created again each time the script runs; it is not a saved Foundry agent.

Try: `What is a Python list?` followed by `How do I add an item?` The example demonstrates interactive input. Agent Framework chat context may depend on the framework's session behavior; this simple example does not explicitly store a session between runs.

### 2. M2_02 — custom Python function tool

```powershell
python demos/m2/M2_02_custom_function_tool.py
```

The `@tool` decorator describes `get_demo_weather` as a callable tool. Its type annotation and `Field` description tell the framework what argument the function expects. Passing `tools=[get_demo_weather]` registers it with the local agent. The model chooses whether it is useful.

Try: `What is the demo weather in Seattle?` and `What is the demo weather in Tokyo?` The function returns a fixed teaching result or explains that a city is unsupported; it never calls a real weather service. `approval_mode="never_require"` is used only for this harmless read-only sample function.

### 3. M2_03 — explicit Foundry function-call cycle

```powershell
python demos/m2/M2_03_foundry_function_calling.py
```

This example focuses on one tool cycle. Enter `Add 18 and 24` and watch these steps: Foundry sends the tool request and arguments; Python calls `add_numbers`; Python returns the result with the original call ID; then the agent explains the result. The script also deletes the temporary agent version and conversation when it finishes. If the model answers without requesting the tool, try asking directly for addition.

### 4–5. M2_04 and M2_05 — MCP server and client

Open two VS Code terminal tabs. Start the server in terminal 1 and leave it running:

```powershell
python demos/m2/M2_04_local_mcp_server.py
```

Run the client in terminal 2:

```powershell
python demos/m2/M2_05_mcp_client_agent.py
```

M2_04 uses the MCP Python SDK v2 API: `from mcp.server.mcpserver import MCPServer`, then `@server.tool()` to publish a deterministic local function. SDK v2 renamed `FastMCP` to `MCPServer` and changed its import path; old v1 snippets that import `mcp.server.fastmcp.FastMCP` fail with the pinned `mcp>=2.2,<3` dependency. M2_05's `MCPStdioTool` starts the server as a child process, discovers its tools, and exposes them to the model-backed agent. Run these two files in order. Try questions about agent, MCP, RAG, and an unsupported topic. Type `quit` in the client; its context manager shuts down the child server. Stop a server started directly with Ctrl+C.

This pair uses a local server so the protocol can be demonstrated without a remote MCP service, project connection, or separate credentials. It models the same discovery/call pattern at local scope.

### 6. M2_06 — Foundry IQ knowledge-base agent

Foundry IQ is Azure AI Search's managed knowledge and retrieval layer. A **knowledge source** identifies content, such as the uploaded `sample_data/expenses_policy.txt`; a **knowledge base** groups one or more sources and retrieval settings; an **MCP endpoint** exposes knowledge-base retrieval as a tool. A Foundry **RemoteTool project connection** links the endpoint to the project using the project's managed identity. The `Microsoft.CognitiveServices/accounts` ARM provider namespace identifies the Foundry project resource family; `Microsoft.Search/searchServices` identifies Azure AI Search. These Azure resource-provider namespaces are not Python code namespaces.

For this demo, create a File knowledge source from `sample_data/expenses_policy.txt`, add it to a knowledge base, create a RemoteTool project connection, grant Search Index Data Reader to the Foundry project's managed identity, and set the `.env` values. The detailed numbered sequence and presenter notes are in `M2_DEMOS_RUN_GUIDE.md` and at the bottom of `M2_06_foundry_iq_agent.py`.

```powershell
python demos/m2/M2_06_foundry_iq_agent.py
```

The script creates a temporary prompt-agent version with only the `knowledge_base_retrieve` MCP tool allowed, sends one question, prints the response, and deletes the conversation and agent version. The Foundry project connection authenticates the service to Search; the Python process does not connect directly to Search. It does not remove your knowledge base, project connection, or source data.

Try a question answered by the knowledge source. A good answer is grounded in retrieved content and should not invent policy details. The demo uses `require_approval="never"` only for the configured read-only retrieval tool.

### 7. M2_07 — sequential multi-agent workflow

```powershell
python demos/m2/M2_07_sequential_agents.py
```

The same chat client creates two local agent objects with different instructions. `SequentialBuilder(participants=[drafter, reviewer])` fixes their order. For each incident description, the drafter summarizes first; then the reviewer sees the prior context and checks the summary. The workflow output comes from the final participant. This demonstrates code-based Agent Framework orchestration; it does not create the visual Foundry workflow shown elsewhere in the deck.

Try entering an incident with known facts and one with missing information. Compare the reviewer output and discuss what should be verified by a person.

### 8. M2_08 — connect to a portal-created prompt agent

First create/configure an agent in the Foundry portal. Put these values in `.env`:

```text
FOUNDRY_AGENT_NAME=<agent-name>
```

Then run:

```powershell
python demos/m2/M2_08_connect_prompt_agent.py
```

This code binds an OpenAI-compatible client to the existing agent name, creates one conversation, and sends user turns until `quit`. The service uses the stored model, instructions, and tool configuration. Changing `AZURE_AI_FOUNDRY_MODEL` does not replace the model on this existing prompt agent. The script deletes only the conversation it created.

## What the comments at the end of each file tell you

The run guides provide commands, sample inputs, and expected behavior. The demo comments point to the main model, Python function, MCP server, or Foundry service step. `common.py` is setup code shared by the other M2 files and is not run directly.

## Common errors

- **Missing settings:** Check the project-root `.env` spelling and ensure there are no placeholder values.
- **Azure CLI credential error:** Run `az login` and check that you selected the right tenant/subscription.
- **401/403:** Verify the project endpoint, signed-in identity's project role, model deployment access, project connection, and Search role assignments.
- **Deployment not found:** Put the deployed model name, not just a model family name, in `AZURE_AI_FOUNDRY_MODEL`.
- **MCP client cannot start server:** Run both commands from the workspace root using the same virtual environment; install requirements first.
- **Agent does not call the tool:** Model selection is probabilistic. Ask a direct question that clearly needs the tool and check that the tool instructions/descriptions are clear.
- **Temporary cloud resource remains:** If the process is force-stopped or the network fails during cleanup, inspect Foundry for the uniquely named `m2-calculator-*` or `m2-foundry-iq-*` version and remove it. The local MCP server has no cloud resources.

## Teaching sequence

A clear live explanation can follow this sequence: first run M2_01 and point to the client, instructions, `run`, and output; then use M2_02 to show a decorated function as a tool; use M2_03 to unpack the model-request/Python-execution/result-return cycle; use M2_04/M2_05 to show that MCP moves tool definitions and execution behind a server protocol; use M2_06 to show retrieval as a knowledge tool; and finish with M2_07 to show two specialized agents passing context in a fixed order. M2_08 connects the code to an agent already configured in the portal.
