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


# M3_04 WALKTHROUGH AND TEST
# 1. AIProjectClient connects to the Foundry project using the signed-in Azure CLI
#    identity. get_openai_client selects the saved agent from .env.
# 2. The conversation loop sends each question to the saved agent and prints its
#    reply. The finally blocks delete only the conversation and close the clients;
#    they do not delete the portal agent.
#
# Configure the Foundry project endpoint, saved agent name, and Speech MCP
# connection first; authenticate with `az login`. From the repository root run:
#   python demos/m3/M3_04_connect_speech_agent.py
# Ask for a short phrase to be spoken or a transcription task supported by the
# configured agent. Expected: the saved agent's response; type quit to exit.
