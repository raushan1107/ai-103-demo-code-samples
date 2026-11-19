"""Ask one question using Foundry IQ as a knowledge tool."""

import json
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from uuid import uuid4

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
from azure.identity import AzureCliCredential
from openai import BadRequestError

from common import required_setting


def diagnostic_endpoint(endpoint: str) -> str:
    """Return the MCP URL without any query values other than api-version."""
    parsed = urlsplit(endpoint)
    api_version = parse_qs(parsed.query).get("api-version", [None])[0]
    query = urlencode({"api-version": api_version}) if api_version else ""
    authority = parsed.netloc.rsplit("@", 1)[-1]
    return urlunsplit((parsed.scheme, authority, parsed.path, query, ""))


def print_bad_request_details(error: BadRequestError) -> None:
    """Print structured service details when the Responses API provides them."""
    print(f"{type(error).__name__} (HTTP {error.status_code}): {error}")
    body = error.body
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
    if isinstance(body, dict):
        details = body.get("error", body)
        print("Service error details:")
        print(json.dumps(details, indent=2, default=str))
    elif body is not None:
        print(f"Service error details: {body}")

# Example setup: use the knowledge-base MCP endpoint and its matching project
# connection, configured for the Foundry project's managed identity.

def main() -> None:
    credential = AzureCliCredential()
    project_endpoint = required_setting("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
    model = required_setting("AZURE_AI_FOUNDRY_MODEL")
    mcp_endpoint = required_setting("FOUNDRY_IQ_MCP_ENDPOINT")
    connection_id = required_setting("FOUNDRY_IQ_CONNECTION_NAME")
    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
    )
    agent = None
    conversation_id = None

    try:
        print("Foundry IQ MCP configuration:")
        print(f"  MCP endpoint: {diagnostic_endpoint(mcp_endpoint)}")
        print(f"  Project connection ID: {connection_id}")
        print(f"  Model deployment: {model}")

        # This MCP tool connects the agent to the already configured knowledge base.
        knowledge_tool = MCPTool(
            server_label="course-knowledge",
            server_url=mcp_endpoint,
            project_connection_id=connection_id,
            allowed_tools=["knowledge_base_retrieve"],
            require_approval="never",  # retrieval is read-only
        )

        # Create a temporary agent that can use only the retrieval tool.
        agent = project.agents.create_version(
            agent_name=f"m2-iq-demo-{uuid4().hex[:8]}",
            definition=PromptAgentDefinition(
                model=model,
                instructions=(
                    "Use the knowledge base to answer. If it does not contain the answer, say so. "
                    "Include source citations when they are returned."
                ),
                tools=[knowledge_tool],
            ),
        )

        question = input("Ask a question covered by the knowledge base: ").strip()
        if not question:
            print("No question entered.")
            return

        with project.get_openai_client(agent_name=agent.name) as client:
            conversation = client.conversations.create()
            conversation_id = conversation.id
            try:
                answer = client.responses.create(input=question, conversation=conversation_id)
            except BadRequestError as error:
                print(
                    "The Responses API rejected the request. Check the MCP endpoint, project "
                    "connection, Foundry project identity permissions, and knowledge base."
                )
                print_bad_request_details(error)
                raise
            print(f"Agent: {answer.output_text}")
    finally:
        # Only the temporary conversation and agent created above are removed.
        if conversation_id and agent:
            with project.get_openai_client(agent_name=agent.name) as client:
                client.conversations.delete(conversation_id=conversation_id)
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        project.close()
        credential.close()


if __name__ == "__main__":
    main()


# Foundry IQ knowledge-base retrieval
#
# What Foundry IQ is:
# Foundry IQ is the knowledge/retrieval layer built on Azure AI Search. It lets
# an agent find relevant pieces of your approved documents and answer from them.
# It is not a model. The model interprets the question and writes the answer;
# Foundry IQ retrieves the supporting information and can return source citations.
#
# Names and what they mean in this demo:
# - Search service: the Azure AI Search resource that stores and retrieves content.
# - Knowledge source: the configured connection to content. For this demo, it is
#   a File source made from sample_data/expenses_policy.txt.
# - Knowledge base: the retrieval resource that contains/references that source.
# - MCP endpoint: the knowledge base's URL for the Model Context Protocol.
# - Project connection: the Foundry project's RemoteTool connection to that URL.
#   Its ProjectManagedIdentity authentication lets Foundry access Search.
# - course-knowledge: the server label the Responses API uses for this MCP tool.
# - knowledge_base_retrieve: the read-only MCP tool the model is allowed to call.
# - Agent name: generated for this run; the script deletes its temporary version.
#
# Python import namespaces used above:
# - azure.ai.projects: creates the client that talks to the Foundry project.
# - azure.ai.projects.models: provides MCPTool and PromptAgentDefinition.
# - azure.identity: AzureCliCredential reuses the identity from `az login`.
# - uuid: creates a unique temporary agent name so concurrent demos do not collide.
# These are Python package namespaces, separate from the Azure resource-provider
# namespaces Microsoft.CognitiveServices/accounts and Microsoft.Search/searchServices.
#
# Step 1 — Prepare the content in Foundry:
# Open Microsoft Foundry (New Foundry experience) and select the project. Go to
# Build > Knowledge. Create or select an Azure AI Search service. Add a File
# knowledge source and upload sample_data/expenses_policy.txt from this project.
# Create a knowledge base and add that source. Give them clear names such as
# m2-expenses-source and m2-expenses-kb, then wait for setup/indexing to finish.
#
# Step 2 — Connect the Foundry project to the knowledge base:
# Copy the knowledge base MCP endpoint. Create a RemoteTool project connection
# targeting that endpoint, using ProjectManagedIdentity authentication. Note its
# exact project connection ID (often the connection name). Grant the project's
# managed identity Search Index Data Reader on the Search service. The user who
# runs this script also needs permission to create/delete Foundry agent versions.
#
# Step 3 — Set local configuration:
# Run `az login`, then put the project endpoint, deployed model name, full
# knowledge-base MCP endpoint, and project connection ID in the root .env file:
# AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=...
# AZURE_AI_FOUNDRY_MODEL=...
# FOUNDRY_IQ_MCP_ENDPOINT=.../knowledgebases/m2-expenses-kb/mcp?api-version=2026-08-01-preview
# FOUNDRY_IQ_CONNECTION_NAME=<Foundry RemoteTool project connection ID>
# The value passed to MCPTool is project_connection_id, not the Search service name.
# Use the knowledge base's name in the endpoint path (not just the source name).
# Use exact values shown in your portal; do not guess an endpoint or API version.
#
# Step 4 — Walk through the code before running it:
# Point out MCPTool: it names the MCP endpoint, connection, and allowed retrieval
# tool. Point out PromptAgentDefinition: it gives the model instructions and
# attaches that tool. The response call sends the learner's question. In the
# service, the agent can request retrieval; Foundry IQ searches the uploaded file
# and the model returns an answer grounded in the retrieved material.
#
# Step 5 — Run the demo from the repository root:
# `python demos/m2/M2_06_foundry_iq_agent.py`
# Ask: "What is the taxi reimbursement limit, and what is required with the claim?"
# Expected: an answer based on the uploaded policy. Ask a question not covered by
# the file to show that the agent should say the source does not answer.
#
# Step 6 — Explain cleanup:
# The finally block deletes only this run's conversation and temporary agent
# version. The Search service, uploaded file/source, knowledge base, and project
# connection remain in Azure. Delete them only when the class no longer needs them.

