"""M2 demo: interact with an existing prompt agent created in Foundry.

Run from the project root: python demos/m2/M2_08_connect_prompt_agent.py
Set AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_AGENT_NAME in .env; run
az login and ensure your identity can use the project and agent.
"""

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

from common import required_setting


def main() -> None:
    credential = AzureCliCredential()
    project = AIProjectClient(
        endpoint=required_setting("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"),
        credential=credential,
    )
    try:
        agent_name = required_setting("FOUNDRY_AGENT_NAME")
        # Binding the SDK client to agent_name routes Responses calls to that agent.
        with project.get_openai_client(agent_name=agent_name) as client:
            conversation = client.conversations.create()
            try:
                print(f"Connected to {agent_name}. Ask questions; type 'quit' to end.")
                while True:
                    question = input("\nYou: ").strip()
                    if question.lower() in {"quit", "exit"}:
                        print("Agent: Goodbye!")
                        break
                    if not question:
                        print("Enter a question, or type 'quit' to leave.")
                        continue

                    # Reusing the same conversation ID gives the service prior-turn context.
                    response = client.responses.create(
                        input=question,
                        conversation=conversation.id,
                    )
                    print(f"Agent: {response.output_text}")
            finally:
                # The conversation is created by this script, so delete it when done.
                client.conversations.delete(conversation_id=conversation.id)
    finally:
        project.close()
        credential.close()


if __name__ == "__main__":
    main()


# Workflow: connect to a named portal agent -> create conversation -> send user turns
# -> service runs stored instructions/tools -> receive text -> delete conversation.
# The agent definition itself is created and managed in the Foundry portal.

# PRESENTER WALKTHROUGH — M2_08 connect to an existing Foundry prompt agent
#
# Concept: this script is a client for an agent that already exists in Microsoft
# Foundry. The agent's model, instructions, and tools stay in the portal; this
# Python program sends messages and displays replies.
#
# Python namespaces in this file:
# - azure.ai.projects: connects to the Foundry project and existing agent.
# - azure.identity: AzureCliCredential uses the signed-in `az login` identity.
# - demos/m2/common.py: reads the project endpoint and agent name from .env.
#
# Step 1 — Create/configure the agent in the portal:
# Open the intended Foundry project, go to Build > Agents, and create or select a
# prompt agent. Choose a deployed model, add simple instructions, and add a tool
# only if the demonstration needs one. Save the agent and test a first question
# plus a follow-up in its playground. Copy the exact agent name from its details.
#
# Step 2 — Prepare this Python client:
# Confirm the project endpoint is in the root .env as
# AZURE_AI_FOUNDRY_PROJECT_ENDPOINT. Set FOUNDRY_AGENT_NAME to the saved agent's
# exact name (this is not the model deployment name). Run `az login` with an
# identity allowed to use the Foundry project and agent.
#
# Step 3 — Walk through the code:
# Point out AIProjectClient: it connects to the Foundry project using Entra ID.
# get_openai_client(agent_name=...) selects the existing portal agent. The script
# creates one conversation, then responses.create sends each user turn with the
# same conversation ID so the agent can use prior-turn context. The finally block
# deletes only that conversation; it does not delete or edit the portal agent.
#
# Step 4 — Run from the repository root:
# `python demos/m2/M2_08_connect_prompt_agent.py`
# Ask a question, then ask a follow-up that depends on the first answer. Type
# `quit` to end. Compare this client result with the portal playground.
#
# Step 5 — Explain ownership:
# Change instructions or tools in the Foundry portal and save the agent there.
# This script only uses the saved configuration; changing the M2 model setting
# in .env does not change the model assigned to this portal agent.
