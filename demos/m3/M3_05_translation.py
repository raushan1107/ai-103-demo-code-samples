"""Translate and transliterate text, then optionally translate speech."""

from azure.ai.translation.text import TextTranslationClient
from azure.ai.translation.text.models import InputTextItem
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk

from common import required_setting


def main() -> None:
    translator = TextTranslationClient(
        endpoint=required_setting("AZURE_TRANSLATOR_ENDPOINT"),
        credential=AzureKeyCredential(required_setting("AZURE_TRANSLATOR_KEY")),
        region=required_setting("AZURE_TRANSLATOR_REGION"),
    )
    text = input("Text to translate from auto-detected language to English: ").strip()
    if text:
        result = translator.translate(body=[InputTextItem(text=text)], to_language=["en"])[0]
        for translation in result.translations:
            print(f"Translation ({translation.to}): {translation.text}")

    source = input("Text to transliterate from Japanese to Latin (Enter to skip): ").strip()
    if source:
        result = translator.transliterate(body=[InputTextItem(text=source)], language="ja", from_script="Jpan", to_script="Latn")[0]
        print(f"Transliteration: {result.text}")

    audio_path = input("Optional WAV file for speech translation (Enter to skip): ").strip()
    if audio_path:
        config = speechsdk.translation.SpeechTranslationConfig(
            subscription=required_setting("AZURE_SPEECH_KEY"),
            endpoint=required_setting("AZURE_SPEECH_ENDPOINT"),
        )
        config.speech_recognition_language = "en-US"
        config.add_target_language("fr")
        audio = speechsdk.audio.AudioConfig(filename=audio_path)
        result = speechsdk.translation.TranslationRecognizer(translation_config=config, audio_config=audio).recognize_once_async().get()
        if result.reason == speechsdk.ResultReason.TranslatedSpeech:
            print(f"Speech transcript: {result.text}")
            print(f"French translation: {result.translations.get('fr', '')}")
        else:
            print(f"No translated speech returned: {result.reason}")


if __name__ == "__main__":
    main()
