"""Responses API function-calling loop grounded by the local verified JSON data."""

import json
import logging
from typing import Any

from app.config import Settings
from app.tools.knowledge_base import KnowledgeBase

logger = logging.getLogger("globalcare.agent")

TOOL_DEFS = [
    {"type":"function","name":"search_hospitals","description":"Search hospitals by city, country or name.","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"],"additionalProperties":False},"strict":True},
    {"type":"function","name":"get_hospital_details","description":"Get verified details for a hospital ID.","parameters":{"type":"object","properties":{"hospital_id":{"type":"string"}},"required":["hospital_id"],"additionalProperties":False},"strict":True},
    {"type":"function","name":"get_department_information","description":"Get department procedure details.","parameters":{"type":"object","properties":{"hospital_id":{"type":"string"},"name":{"type":"string"}},"required":["hospital_id","name"],"additionalProperties":False},"strict":True},
    {"type":"function","name":"get_opening_hours","description":"Get opening hours at a hospital.","parameters":{"type":"object","properties":{"hospital_id":{"type":"string"},"department":{"type":"string"}},"required":["hospital_id","department"],"additionalProperties":False},"strict":True},
    {"type":"function","name":"get_supported_languages","description":"Get supported languages for a hospital.","parameters":{"type":"object","properties":{"hospital_id":{"type":"string"}},"required":["hospital_id"],"additionalProperties":False},"strict":True},
    {"type":"function","name":"search_faq","description":"Search administrative frequently asked questions.","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"],"additionalProperties":False},"strict":True},
]


def respond(question: str, settings: Settings, kb: KnowledgeBase | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Let the model select KB tools, execute only registered functions, and ground its response."""
    from openai import OpenAI

    if not all((settings.model_endpoint, settings.model_key, settings.model_deployment)):
        raise RuntimeError("Configure Foundry model endpoint, key and deployment first.")
    kb = kb or KnowledgeBase()
    client = OpenAI(base_url=settings.model_endpoint, api_key=settings.model_key)
    trace: list[dict[str, Any]] = []
    try:
        response = client.responses.create(model=settings.model_deployment, instructions=(
            "You are GlobalCare's administrative reception assistant. Use the knowledge tools for factual hospital questions. "
            "Never invent missing details. Say when the verified data has no answer. Do not diagnose or recommend treatment."
        ), input=question, tools=TOOL_DEFS, max_output_tokens=500)
        for _ in range(5):
            calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
            if not calls:
                return response.output_text, trace
            outputs = []
            for call in calls:
                args = json.loads(call.arguments)
                logger.info("tool request name=%s arguments=%s", call.name, args)
                result = kb.execute(call.name, args)
                record = {"tool": call.name, "arguments": args, "result": result}
                trace.append(record)
                logger.info("tool result name=%s result=%s", call.name, result)
                outputs.append({"type":"function_call_output", "call_id":call.call_id, "output":json.dumps(result, ensure_ascii=False)})
            response = client.responses.create(model=settings.model_deployment, previous_response_id=response.id, input=outputs, tools=TOOL_DEFS, max_output_tokens=500)
        raise RuntimeError("Agent exceeded five tool rounds; inspect the trace and prompt.")
    finally:
        client.close()
