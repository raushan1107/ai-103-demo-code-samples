"""M2 demo: run two Agent Framework agents one after the other.

Run from the project root: python demos/m2/M2_07_sequential_agents.py
Requires AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_FOUNDRY_MODEL in .env,
az login, and project/model access.
"""

import asyncio

from agent_framework.orchestrations import SequentialBuilder

from common import foundry_chat_client


async def main() -> None:
    # One client configuration can create multiple agents using the same model.
    client = foundry_chat_client()
    drafter = client.as_agent(
        name="incident-drafter",
        instructions=(
            "Write a concise incident summary using only the user's notes. "
            "Clearly mark facts that are missing; do not invent them."
        ),
    )
    reviewer = client.as_agent(
        name="incident-reviewer",
        instructions=(
            "Review the previous agent's incident summary. Return a corrected concise version "
            "and list any missing facts that should be confirmed."
        ),
    )

    # Participant order defines the workflow: drafter first, reviewer second.
    workflow = SequentialBuilder(participants=[drafter, reviewer]).build()
    print("Incident workflow is ready. Enter incident notes, or type 'quit' to stop.")

    while True:
        notes = input("\nIncident notes: ").strip()
        if notes.lower() in {"quit", "exit"}:
            print("Workflow: Goodbye!")
            break
        if not notes:
            print("Enter notes, or type 'quit' to leave.")
            continue

        # The workflow runs each participant in order. The second agent receives context
        # from the first and provides the terminal output collected below.
        events = await workflow.run(notes)
        outputs = events.get_outputs()
        if not outputs:
            print("The workflow returned no final output.")
            continue

        print("\nReviewed summary:")
        for message in outputs[0].messages:
            print(message.text)


if __name__ == "__main__":
    asyncio.run(main())


# Try: Checkout failed for about five minutes after a database restart. Service recovered.
# Then enter a different incident. Type quit to stop.
# Workflow: incident notes -> drafter agent -> draft/context -> reviewer agent -> final response.

# PRESENTER WALKTHROUGH — M2_07 Sequential Agent Framework workflow
#
# Concept: a sequential workflow sends the same task through specialized agents
# in a fixed order. This example uses two local Agent Framework agents (they are
# Python objects for this run, not saved portal agents):
# incident-drafter writes a concise factual summary; incident-reviewer checks it
# and identifies missing facts. The model deployment is shared by both.
#
# Python namespaces in this file:
# - agent_framework.orchestrations: provides SequentialBuilder for agent order.
# - demos/m2/common.py: loads .env and creates the Foundry chat client.
# The workflow and its two agents run in this Python process; they are not saved
# as Azure portal resources under the Microsoft.CognitiveServices namespace.
#
# Step 1 — Prepare Foundry access:
# In Microsoft Foundry, open the project and confirm it has a deployed chat model.
# Copy the project endpoint and exact deployment name into the root .env as
# AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_FOUNDRY_MODEL. Run `az login`.
# No knowledge source, MCP connection, or portal agent is needed for this demo.
#
# Step 2 — Walk through the code:
# Point out foundry_chat_client(): it supplies the project endpoint, model, and
# Azure CLI identity. Point out the two as_agent() calls: each agent has its own
# name and instructions. Point out SequentialBuilder(participants=[drafter,
# reviewer]): list order is run order. The reviewer receives the earlier context.
# Finally, workflow.run(notes) starts the pipeline and get_outputs() collects the
# last agent's response. Nothing is saved as an Azure agent resource.
#
# Step 3 — Run from the repository root:
# `python demos/m2/M2_07_sequential_agents.py`
# Enter: Checkout failed for about five minutes after a database restart. Service recovered. 
# Type `quit` when you have seen the result.
#
# Step 4 — Explain the result:
# The first agent drafts; the second checks it. Compare the final wording with the
# original notes. Ask which facts are missing (for example, customer impact or
# exact recovery time). The model can still make mistakes, so a person should
# verify incident facts before using the summary.
