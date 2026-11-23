"""Azure Text Translation service wrapper."""

from azure.ai.translation.text import TextTranslationClient
from azure.ai.translation.text.models import InputTextItem
from azure.core.credentials import AzureKeyCredential

from app.config import Settings


def _client(settings: Settings) -> TextTranslationClient:
    if not settings.translator_key or not settings.translator_region:
        raise RuntimeError("Configure GC_TRANSLATOR_KEY and GC_TRANSLATOR_REGION.")
    return TextTranslationClient(
        endpoint=settings.translator_endpoint,
        credential=AzureKeyCredential(settings.translator_key),
        region=settings.translator_region,
    )


def translate(text: str, targets: list[str], source: str | None, settings: Settings) -> list[dict[str, str]]:
    """Translate one source text to one or more target language codes."""
    if not targets:
        raise ValueError("At least one target language is required.")
    client = _client(settings)
    try:
        result = client.translate([InputTextItem(text=text)], to_language=targets, from_language=source)[0]
        return [{"language": item.to, "text": item.text} for item in result.translations]
    finally:
        client.close()


def supported_languages(settings: Settings) -> dict[str, object]:
    """Fetch the service capability list. Callers should cache this response."""
    client = _client(settings)
    try:
        result = client.get_supported_languages(scope="translation,transliteration")
        translation = {
            code: {"name": item.name, "native_name": item.native_name}
            for code, item in (result.translation or {}).items()
        }
        transliteration = {
            code: {
                "name": item.name,
                "native_name": item.native_name,
                "scripts": [
                    [
                        {"code": target.code, "name": target.name, "native_name": target.native_name}
                        for target in script.to_scripts
                    ]
                    for script in item.scripts
                ],
            }
            for code, item in (result.transliteration or {}).items()
        }
        return {"translation": translation, "transliteration": transliteration}
    finally:
        client.close()


def transliterate(text: str, language: str, from_script: str, to_script: str, settings: Settings) -> str:
    """Convert characters between writing systems without translating meaning."""
    client = _client(settings)
    try:
        result = client.transliterate([InputTextItem(text=text)], language=language, from_script=from_script, to_script=to_script)[0]
        return result.text
    finally:
        client.close()
