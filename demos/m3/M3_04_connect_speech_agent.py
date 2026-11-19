"""Connect to a portal-created Azure Speech MCP prompt agent."""

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
        agent_name = required_setting("FOUNDRY_SPEECH_AGENT_NAME")
        with project.get_openai_client(agent_name=agent_name) as client:
            conversation = client.conversations.create()
            try:
                print(f"Connected to {agent_name}. Type 'quit' to end.")
                while True:
                    question = input("\nYou: ").strip()
                    if question.lower() in {"quit", "exit"}:
                        break
                    if question:
                        response = client.responses.create(input=question, conversation=conversation.id)
                        print(f"Agent: {response.output_text}")
            finally:
                client.conversations.delete(conversation_id=conversation.id)
    finally:
        project.close()
        credential.close()


if __name__ == "__main__":
    main()
