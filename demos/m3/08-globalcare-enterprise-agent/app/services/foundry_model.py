"""Small Module 1 Responses API example using an OpenAI-compatible Foundry endpoint."""

from openai import OpenAI

from app.config import Settings


def answer(question: str, context: str, settings: Settings) -> str:
    """Generate a grounded administrative answer; context contains verified KB results."""
    if not all((settings.model_endpoint, settings.model_key, settings.model_deployment)):
        raise RuntimeError("Configure GC_FOUNDRY_MODEL_ENDPOINT, GC_FOUNDRY_MODEL_KEY and GC_FOUNDRY_MODEL_DEPLOYMENT.")
    client = OpenAI(base_url=settings.model_endpoint, api_key=settings.model_key)
    try:
        response = client.responses.create(
            model=settings.model_deployment,
            instructions=("You are GlobalCare's administrative information assistant. Use only the supplied verified context. "
                          "If it does not answer the request, say the information is unavailable. Never give medical diagnosis or treatment advice."),
            input=f"Verified context:\n{context}\n\nUser request:\n{question}",
            max_output_tokens=400,
        )
        return response.output_text
    finally:
        client.close()
