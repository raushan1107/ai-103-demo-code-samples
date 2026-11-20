"""Run a local tool-calling assistant with a Foundry model and Azure Language."""

import json

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from common import configure_console_encoding, foundry_client, required_setting

INSTRUCTIONS = (
    "You are a concise language-analysis assistant. For each user message, call "
    "detect_language, recognize_entities, and recognize_pii before answering. "
    "Report PII counts and categories only, never PII values. Explain the analysis "
    "briefly and answer in the user's language."
)

TOOLS = [
    {
        "type": "function",
        "name": "detect_language",
        "description": "Detect the language of the supplied text.",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "recognize_entities",
        "description": "Find named entities such as people, organizations, and places.",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "recognize_pii",
        "description": "Find PII and return only categories and redacted text.",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def run_language_tool(name: str, arguments: str, client: TextAnalyticsClient) -> dict:
    """Validate a model tool call and execute its matching local Language operation."""
    parsed_arguments = json.loads(arguments)
    text = parsed_arguments.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{name} requires non-empty text.")

    if name == "detect_language":
        result = client.detect_language([text])[0]
        if result.is_error:
            raise RuntimeError(f"Language detection failed: {result.error}")
        return {
            "language": result.primary_language.name,
            "iso6391": result.primary_language.iso6391_name,
        }

    if name == "recognize_entities":
        result = client.recognize_entities([text])[0]
        if result.is_error:
            raise RuntimeError(f"Entity extraction failed: {result.error}")
        return {
            "entities": [
                {
                    "text": entity.text,
                    "category": entity.category,
                    "subcategory": entity.subcategory,
                }
                for entity in result.entities
            ]
        }

    if name == "recognize_pii":
        result = client.recognize_pii_entities([text])[0]
        if result.is_error:
            raise RuntimeError(f"PII detection failed: {result.error}")
        return {
            "count": len(result.entities),
            "categories": sorted({entity.category for entity in result.entities}),
            "redacted_text": result.redacted_text,
        }

    raise ValueError(f"Unknown Language tool: {name}")


def main() -> None:
    configure_console_encoding()
    model_client, model = foundry_client()
    language_client = TextAnalyticsClient(
        endpoint=required_setting("AZURE_LANGUAGE_ENDPOINT"),
        credential=AzureKeyCredential(required_setting("AZURE_LANGUAGE_KEY")),
    )
    history = []

    print("Local Language assistant ready. Use synthetic text; type 'quit' to end.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue

        history.append({"role": "user", "content": question})
        for _ in range(5):
            response = model_client.responses.create(
                model=model,
                instructions=INSTRUCTIONS,
                input=history,
                tools=TOOLS,
            )
            history.extend(response.output)
            tool_calls = [item for item in response.output if item.type == "function_call"]
            if not tool_calls:
                print(f"Assistant: {response.output_text}")
                break

            for call in tool_calls:
                print(f"Local tool: {call.name}")
                result = run_language_tool(call.name, call.arguments, language_client)
                history.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(result, ensure_ascii=False),
                    }
                )
        else:
            raise RuntimeError("The model did not finish after five tool-call rounds.")


if __name__ == "__main__":
    main()


# M3_03 WALKTHROUGH AND TEST
# 1. INSTRUCTIONS and TOOLS tell the Foundry model which local functions it can
#    request and how to summarize their results.
# 2. run_language_tool validates each function call and invokes Azure Language
#    for detection, entity extraction, or PII detection.
# 3. main() keeps conversation history, dispatches model-requested tools, sends
#    results back to the model, and prints its final answer. It creates no saved
#    portal agent. PII results omit detected values, but the original prompt is
#    still sent to the configured model; use synthetic text only.
#
# From the repository root run:
#   python demos/m3/M3_03_local_language_agent.py
# Ask: Asha Rao at Contoso in Pune can be reached at asha@example.com. What did I say?
# Expected: Local tool lines for detection, entities, and PII, followed by a concise
# summary with the language and PII categories. Type quit to end the conversation.
