"""Create a temporary Foundry prompt agent with local, read-only GlobalCare tools."""

import json
import logging
from typing import Any
from uuid import uuid4

from app.config import Settings
from app.tools.knowledge_base import KnowledgeBase

logger = logging.getLogger("globalcare.foundry_agent")

SCHEMAS: dict[str, dict[str, Any]] = {
    "search_hospitals": {"description":"Search fictional hospitals by city, country or name.","properties":{"query":{"type":"string"}},"required":["query"]},
    "get_hospital_details": {"description":"Get details for a known hospital ID.","properties":{"hospital_id":{"type":"string"}},"required":["hospital_id"]},
    "get_department_information": {"description":"Get department procedure information.","properties":{"hospital_id":{"type":"string"},"name":{"type":"string"}},"required":["hospital_id","name"]},
    "get_opening_hours": {"description":"Get opening hours at a hospital.","properties":{"hospital_id":{"type":"string"},"department":{"type":"string"}},"required":["hospital_id","department"]},
    "get_supported_languages": {"description":"List languages supported at a hospital.","properties":{"hospital_id":{"type":"string"}},"required":["hospital_id"]},
    "search_faq": {"description":"Search administrative FAQs.","properties":{"query":{"type":"string"}},"required":["query"]},
}


def respond(question: str, settings: Settings, kb: KnowledgeBase | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Use Foundry Agent Service and execute each requested tool against local JSON."""
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
    from azure.identity import AzureCliCredential
    from openai.types.responses.response_input_param import FunctionCallOutput

    if not settings.project_endpoint or not settings.model_deployment:
        raise RuntimeError("Configure GC_FOUNDRY_PROJECT_ENDPOINT and GC_FOUNDRY_MODEL_DEPLOYMENT.")
    kb = kb or KnowledgeBase()
    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=settings.project_endpoint, credential=credential)
    name = f"globalcare-demo-{uuid4().hex[:8]}"
    agent = None
    conversation_id = None
    trace: list[dict[str, Any]] = []
    try:
        tools = [FunctionTool(name=n, description=s["description"], parameters={"type":"object","properties":s["properties"],"required":s["required"],"additionalProperties":False}, strict=True) for n,s in SCHEMAS.items()]
        agent = project.agents.create_version(agent_name=name, definition=PromptAgentDefinition(
            model=settings.model_deployment,
            instructions=("You are GlobalCare's administrative reception assistant. Use tools for factual hospital data. "
                         "Never invent details; state when information is unavailable. Never diagnose or recommend treatment."),
            tools=tools,
        ))
        with project.get_openai_client(agent_name=agent.name) as client:
            conversation = client.conversations.create()
            conversation_id = conversation.id
            response = client.responses.create(input=question, conversation=conversation_id)
            for _ in range(5):
                calls = [item for item in response.output if item.type == "function_call"]
                if not calls:
                    return response.output_text, trace
                outputs = []
                for call in calls:
                    args = json.loads(call.arguments)
                    result = kb.execute(call.name, args)
                    trace.append({"tool":call.name,"arguments":args,"result":result})
                    logger.info("tool=%s arguments=%s result=%s", call.name, args, result)
                    outputs.append(FunctionCallOutput(type="function_call_output", call_id=call.call_id, output=json.dumps(result, ensure_ascii=False)))
                response = client.responses.create(input=outputs, conversation=conversation_id)
            raise RuntimeError("Agent exceeded five tool rounds; inspect prompts and trace.")
    finally:
        if conversation_id and agent:
            with project.get_openai_client(agent_name=agent.name) as client:
                client.conversations.delete(conversation_id=conversation_id)
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        project.close()
        credential.close()
