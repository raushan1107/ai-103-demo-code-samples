# Module 2 demo run guide

The files in `demos/m2/` cover the Python or client-code portions of the Module 2 exercises. For a conceptual, step-by-step walkthrough, see [M2 agent build and workflow guide](M2_AGENT_BUILD_AND_WORKFLOW_GUIDE.md). Open the project root in VS Code and run commands from its integrated terminal.

## Install and configure

1. Use Python 3.10 or later. Create/activate the project's virtual environment as described in the README.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Sign in to the Azure account with access to the Foundry project: `az login`.
4. Add these values to the project-root `.env` file. They are different from M1's `AZURE_AI_FOUNDRY_ENDPOINT` and `AZURE_AI_FOUNDRY_API_KEY`: M2 connects to the Foundry **project endpoint** and authenticates with Entra ID via `az login`.

   ```text
   AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
   AZURE_AI_FOUNDRY_MODEL=<model-deployment-name>
   ```

5. The project endpoint and model are Foundry project values. `AZURE_AI_FOUNDRY_MODEL` must be the deployment name. The identity selected by `az login` needs access to the project and model.

The Agent Framework package uses the current `FoundryChatClient` API. No temperature or other optional sampling setting is included. Model compatibility, project roles, deployment, region, and service features still depend on the Foundry resource.

## VS Code and first agent

The deck's initial VS Code exercise includes portal/extension configuration as well as client code. The Python file demonstrates the client-side agent interaction; it does not install extensions or create Azure resources.

```powershell
python demos/m2/M2_01_first_agent.py
```

Expected: the tutor responds to each question until you type `quit`.

## Custom function tool

`M2_02_custom_function_tool.py` demonstrates the concise Agent Framework pattern: a typed Python function is registered as a tool and the agent chooses when to call it. The weather values are explicitly fictional and fixed.

```powershell
python demos/m2/M2_02_custom_function_tool.py
```

Expected: the agent may use `get_demo_weather` for Seattle and labels the response as sample data. Ask repeatedly until `quit`; no weather API is called.

## Foundry function calling

`M2_03_foundry_function_calling.py` shows one short tool cycle: the agent requests `add_numbers`, Python adds the values, then the agent explains the result.

```powershell
python demos/m2/M2_03_foundry_function_calling.py
```

Enter `Add 18 and 24`. The script creates one temporary agent version and conversation, then deletes them when it exits. If execution is interrupted, check Foundry for resources left behind.

## MCP client and local server

This runnable pair keeps the protocol visible without relying on a public remote MCP endpoint. The M2_05 client starts M2_04 as a child process and discovers its fixed, read-only teaching tool; no separate server terminal is needed. The project pins MCP SDK v2 (`mcp>=2.2,<3`): examples using v1's `FastMCP` import must be migrated to v2's `MCPServer` import.

```powershell
python demos/m2/M2_05_mcp_client_agent.py
```

Expected: the client discovers and calls `lookup_course_topic` from the local MCP server, then summarizes its result. Ask more than one question; type `quit` to exit. The client closes its child server automatically.

## Foundry IQ knowledge-base retrieval

This example requires an already provisioned Azure AI Search knowledge base and a Foundry project connection to that knowledge-base MCP endpoint. Creating the knowledge source, knowledge base, project connection, data permissions, and model deployment is Azure resource setup; the script only creates/invokes/deletes a temporary agent version and conversation.

### Portal setup steps (complete once per project)

1. In Microsoft Foundry's new experience, select the project and open **Build > Knowledge**. Create or select an Azure AI Search service that supports agentic retrieval.
2. Create a **File** knowledge source and upload the repository sample `sample_data/expenses_policy.txt`. This short policy says taxi rides are reimbursable up to USD 75 per trip and claims need a business purpose and receipt. Give the source a clear name, such as `m2-expenses-source`.
3. Create a knowledge base, add that source, and name it `m2-expenses-kb`. Wait until setup/indexing completes. A knowledge source defines where the content comes from; a knowledge base combines sources and retrieval settings into a reusable retrieval endpoint.
4. Copy the full knowledge-base MCP endpoint. For current Microsoft Foundry agent connection instructions, the endpoint uses `api-version=2026-08-01-preview`; use the exact endpoint shown by the portal/docs if that changes.
5. Add a **RemoteTool** project connection to the Foundry project that targets the knowledge-base MCP endpoint and authenticates with **ProjectManagedIdentity**. Put the exact project connection ID in `.env`; do not put the Search service name there. The Python SDK passes this value as `MCPTool.project_connection_id`.
6. Enable the Foundry project's system-assigned managed identity and grant it **Search Index Data Reader** on the Search service. The signed-in learner also needs permission to use the project and create/delete temporary agent versions.
7. Verify the project has a deployed model and that `az login` selected the intended tenant/subscription. Put the project endpoint/model and knowledge-base MCP endpoint/project connection ID in the root `.env` as shown below.
8. Walk through `M2_06_foundry_iq_agent.py` using the presenter notes at the bottom of the file, then run it and ask: `What is the taxi reimbursement limit, and what is required with the claim?` The script deletes its temporary agent version and conversation. The uploaded file, knowledge source, knowledge base, Search service, and project connection remain provisioned.

If the portal uses different labels, use the current Microsoft Foundry IQ and Azure AI Search knowledge-base MCP instructions for your tenant/region. Confirm the tool is read-only before setting approval to `never`.

Add these values to `.env`:

```text
FOUNDRY_IQ_MCP_ENDPOINT=https://<search-service>.search.windows.net/knowledgebases/<knowledge-base>/mcp?api-version=2026-08-01-preview
FOUNDRY_IQ_CONNECTION_NAME=<Foundry RemoteTool project connection ID>
```

The signed-in identity needs permission to create/delete Foundry agent versions. The Foundry project needs a RemoteTool project connection configured with the project managed identity, and that identity needs **Search Index Data Reader** on the Search service. Confirm the knowledge base and source have finished indexing, and that Search network settings (including public network access, if required by the setup) allow Foundry to reach it. If testing the MCP endpoint directly as the signed-in user, that user also needs the applicable Search data role and network access; this does not test the Foundry project's managed identity. For Foundry IQ's read-only `knowledge_base_retrieve` MCP tool, the script uses the current Microsoft configuration with `require_approval="never"`; do not repurpose this setting for tools that change data or trigger external actions. On failure it prints the sanitized MCP endpoint, connection ID, model deployment, and any structured Responses API error details.

```powershell
python demos/m2/M2_06_foundry_iq_agent.py
```

Ask one question covered by `expenses_policy.txt`. The agent should answer from retrieved content or report that the source did not answer. The run order is: create/search service > upload file as source > add source to knowledge base > create project connection > set `.env` > walk the code > run command. See the numbered comments at the bottom of `M2_06_foundry_iq_agent.py` for the live presentation script.

## Sequential multi-agent workflow

This is a code-based workflow; the two agents are created in Python for the current run, so there is no portal agent to create. The names `incident-drafter` and `incident-reviewer` label those two roles. See the numbered presenter notes at the bottom of `M2_07_sequential_agents.py`.

```powershell
python demos/m2/M2_07_sequential_agents.py
```

Enter a brief incident description. Repeat with another description or type `quit`. The drafter creates a short summary, then the reviewer receives the preceding context and produces a checked version. This uses the current `SequentialBuilder` Agent Framework API.

## Connect to an existing portal agent

### Portal setup steps

1. In the Foundry project, open **Agents** and create/open a prompt agent that you are allowed to use.
2. Choose a deployed model; add instructions and any supported tools in the portal, then save the agent.
3. In the playground, test a normal question and a follow-up. Note the agent's exact name from its details page; do not use the model deployment name here.
4. Ensure the signed-in Azure identity has permission to access the project and agent. Run `az login` and select the same tenant/subscription.
5. Add the exact agent name to `.env`, then run the Python client below. The client creates and deletes its own conversation; it does not modify the saved agent.

Configure an existing prompt agent's name in `.env`:

```text
FOUNDRY_AGENT_NAME=<agent-name>
```

Then run:

```powershell
python demos/m2/M2_08_connect_prompt_agent.py
```

The script connects to the existing agent endpoint and uses one conversation for all turns until you type `quit`. The agent's model, instructions, and hosted tools remain the server-side configuration. This demonstrates the client portion of the VS Code exercise, not portal provisioning.

For the live walkthrough, use the numbered notes at the bottom of `M2_08_connect_prompt_agent.py`: configure and test the agent in the portal first, copy its exact name into `.env`, then run the client and ask a follow-up question.

## Not standalone Python demos

Microsoft Foundry Toolkit extension installation and UI, agent publishing to Teams or Microsoft 365, Work IQ integration, and visual Foundry workflow design are portal/extension workflows. The local sequential Python example demonstrates the code-based orchestration concept, but does not create or deploy a visual Foundry workflow. The Azure Language and Speech content is in the separate decks and is outside this Module 2 set.

## Find the `.env` values

Open the project root `.env` in VS Code. The file is ignored by Git. For M2, sign in with `az login`; do not copy the API key used by M1. In Foundry, open the project's **Overview/Details** page and copy its project endpoint to `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`. Open the **Models/Deployments** page and copy the deployment name (not the model family) to `AZURE_AI_FOUNDRY_MODEL`. For `FOUNDRY_AGENT_NAME`, copy the saved prompt agent's name from **Agents**. For Foundry IQ, copy the full knowledge-base MCP endpoint from Azure AI Search and the RemoteTool project connection ID from the Foundry project's connected resources page. Ensure the endpoint path names the knowledge base, not only its source. Keep API keys, passwords, and SAS URLs secret; do not paste them in chat or source code. `.env` is local configuration and is not generated automatically.

## Troubleshooting

- `CredentialUnavailableError`: run `az login`, select the right tenant/subscription, then retry.
- 401/403: check project endpoint, deployment, Entra role assignment, and any Search/connection role assignments.
- Deployment/model error: use the exact deployed model name from the Foundry project.
- MCP server fails to start: run from the project root in the same Python environment used to install `mcp` and `agent-framework-foundry`.
- Tool is not called: restate the tool's intended use in the prompt; model tool selection is not deterministic.
- Service reports unsupported protocol/feature: confirm the configured deployment and API feature support in the project. The local MCP example avoids this dependency; Foundry IQ retrieval needs the documented MCP endpoint and project connection.
- Cleanup reports an error: check whether the temporary conversation or agent version remains in Foundry and delete it manually if needed.
