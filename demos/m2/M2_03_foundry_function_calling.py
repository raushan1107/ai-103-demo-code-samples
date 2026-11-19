"""One simple example of the model asking Python to use a tool."""

import json
from uuid import uuid4

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from azure.identity import AzureCliCredential
from openai.types.responses.response_input_param import FunctionCallOutput

from common import required_setting


def add_numbers(a: int, b: int) -> int:
    """The local function that Python runs when the agent requests it."""
    return a + b


def main() -> None:
    credential = AzureCliCredential()
    project = AIProjectClient(
        endpoint=required_setting("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"),
        credential=credential,
    )
    agent_name = f"m2-add-demo-{uuid4().hex[:8]}"
    agent = None
    conversation_id = None

    try:
        # This small schema tells the model what Python function is available.
        add_tool = FunctionTool(
            name="add_numbers",
            description="Add two whole numbers.",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
            strict=True,
        )

        agent = project.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=required_setting("AZURE_AI_FOUNDRY_MODEL"),
                instructions="Use add_numbers for addition. Explain the result in one sentence.",
                tools=[add_tool],
            ),
        )

        # Ask one question so we can see the full tool handoff in order.
        question = input("Ask me to add two numbers (example: Add 18 and 24): ").strip()
        if not question:
            print("No question entered.")
            return

        with project.get_openai_client(agent_name=agent.name) as client:
            conversation = client.conversations.create()
            conversation_id = conversation.id
            response = client.responses.create(input=question, conversation=conversation_id)

            # The model can answer with text or ask Python to call add_numbers.
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                print(f"Agent: {response.output_text}")
                return

            results = []
            for call in calls:
                arguments = json.loads(call.arguments)
                total = add_numbers(arguments["a"], arguments["b"])
                print(f"Python ran: {arguments['a']} + {arguments['b']} = {total}")
                results.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=call.call_id,
                        output=json.dumps({"result": total}),
                    )
                )

            # Return Python's result using the call ID so the agent can finish.
            final = client.responses.create(input=results, conversation=conversation_id)
            print(f"Agent: {final.output_text}")
    finally:
        # These are temporary demo resources. Delete them when the script ends.
        if conversation_id and agent:
            with project.get_openai_client(agent_name=agent.name) as client:
                client.conversations.delete(conversation_id=conversation_id)
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        project.close()
        credential.close()


if __name__ == "__main__":
    main()
