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
