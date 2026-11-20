"""Detect language, named entities, and PII with Azure AI Language."""

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from common import required_setting


def main() -> None:
    client = TextAnalyticsClient(
        endpoint=required_setting("AZURE_LANGUAGE_ENDPOINT"),
        credential=AzureKeyCredential(required_setting("AZURE_LANGUAGE_KEY")),
    )
    print("Enter synthetic sample text for language, entity, and PII analysis.")
    text = input("Text: ").strip()
    if not text:
        print("No text entered.")
        return

    language = client.detect_language([text])[0]
    print(f"Language: {language.primary_language.name} ({language.primary_language.iso6391_name})")
    entities = client.recognize_entities([text])[0]
    print("Entities:")
    for entity in entities.entities:
        print(f"- {entity.text}: {entity.category} / {entity.subcategory or 'unspecified'}")
    pii = client.recognize_pii_entities([text])[0]
    print("PII detections (text is not redacted):")
    for entity in pii.entities:
        print(f"- {entity.category}: {entity.text}")


if __name__ == "__main__":
    main()


# M3_01 WALKTHROUGH AND TEST
# 1. TextAnalyticsClient uses the Language endpoint and key from .env.
# 2. The prompt reads one text sample; an empty line exits without an API call.
# 3. detect_language reports the language, recognize_entities lists named
#    entities, and recognize_pii_entities lists detected PII categories/spans.
#    This introductory script does not redact the submitted text.
#
# From the repository root run:
#   python demos/m3/M3_01_language_analysis.py
# Enter: Asha Rao works at Contoso in Pune. Contact asha@example.com.
# Expected: English detection and entity/PII results; exact entities can vary.
# Use synthetic text only; the Language service may miss sensitive spans.
