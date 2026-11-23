"""Translate one microphone turn to multiple target text languages."""

import azure.cognitiveservices.speech as speechsdk
from pathlib import Path

from speech_config import speech_settings


def main() -> None:
    key, region = speech_settings()
    source = input("Source speech language [en-US]: ").strip() or "en-US"
    targets = input("Target language codes, comma separated [hi,ja]: ").strip() or "hi,ja"
    target_languages = [item.strip() for item in targets.split(",") if item.strip()]
    if not target_languages:
        raise ValueError("Enter at least one target language code.")

    config = speechsdk.translation.SpeechTranslationConfig(subscription=key, region=region)
    config.speech_recognition_language = source
    for language in target_languages:
        config.add_target_language(language)
    source_audio = input("Optional WAV file (Enter to use microphone): ").strip()
    audio_config = (speechsdk.audio.AudioConfig(filename=str(Path(source_audio))) if source_audio
                    else speechsdk.audio.AudioConfig(use_default_microphone=True))
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=config,
        audio_config=audio_config,
    )
    print("Speak one short sentence after the prompt." if not source_audio else f"Reading {source_audio}")
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        print(f"Transcript ({source}): {result.text}")
        for language in target_languages:
            print(f"{language}: {result.translations.get(language, '(no translation returned)')}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print(f"NoMatch: {result.no_match_details}")
    else:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(f"Speech translation canceled: {details.reason}; {details.error_details}")


if __name__ == "__main__":
    main()
