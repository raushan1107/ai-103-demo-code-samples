"""Prebuilt Azure AI Language analysis; no generative model is used here."""

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from app.config import Settings


def analyze(text: str, settings: Settings) -> dict[str, object]:
    """Detect language, entities, and PII; return only categories and redacted text for PII."""
    if not settings.language_endpoint or not settings.language_key:
        raise RuntimeError("Configure GC_LANGUAGE_ENDPOINT and GC_LANGUAGE_KEY.")
    client = TextAnalyticsClient(endpoint=settings.language_endpoint, credential=AzureKeyCredential(settings.language_key))
    try:
        language = client.detect_language([text])[0]
        entities = client.recognize_entities([text])[0]
        pii = client.recognize_pii_entities([text])[0]
        for result in (language, entities, pii):
            if result.is_error:
                raise RuntimeError(str(result.error))
        return {
            "language": {"name": language.primary_language.name, "code": language.primary_language.iso6391_name},
            "entities": [{"category": item.category, "subcategory": item.subcategory} for item in entities.entities],
            "pii_categories": sorted({item.category for item in pii.entities}),
            "pii_count": len(pii.entities),
            "redacted_text": pii.redacted_text,
        }
    finally:
        client.close()
