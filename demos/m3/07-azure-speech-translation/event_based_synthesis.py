"""Translate microphone speech and save target speech from the Synthesizing event."""

from typing import Any
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from speech_config import audio_output, speech_settings


def main() -> None:
    key, region = speech_settings()
    source = input("Source speech language [en-US]: ").strip() or "en-US"
    target = input("Single target language [fr]: ").strip() or "fr"
    if "," in target:
        raise ValueError("Event-based synthesis supports one target language. Use manual_synthesis.py for multiple languages.")
    voice = input("Target neural voice [fr-FR-DeniseNeural]: ").strip() or "fr-FR-DeniseNeural"
    config = speechsdk.translation.SpeechTranslationConfig(subscription=key, region=region)
    config.speech_recognition_language = source
    config.add_target_language(target)
    config.voice_name = voice
    source_audio = input("Optional WAV file (Enter to use microphone): ").strip()
    audio_config = (speechsdk.audio.AudioConfig(filename=str(Path(source_audio))) if source_audio
                    else speechsdk.audio.AudioConfig(use_default_microphone=True))
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=config,
        audio_config=audio_config,
    )
    output = audio_output(f"event-{target}.wav")
    chunks: list[bytes] = []
    def on_synthesizing(event: Any) -> None:
        audio = event.result.audio
        if audio:
            chunks.append(audio)

    recognizer.synthesizing.connect(on_synthesizing)
    try:
        print("Speak one short sentence." if not source_audio else f"Reading {source_audio}")
        result = recognizer.recognize_once_async().get()
        if result.reason == speechsdk.ResultReason.TranslatedSpeech:
            print(f"Transcript: {result.text}")
            print(f"{target}: {result.translations.get(target, '')}")
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print(f"NoMatch: {result.no_match_details}")
            return
        else:
            details = speechsdk.CancellationDetails.from_result(result)
            raise RuntimeError(f"Speech translation canceled: {details.reason}; {details.error_details}")
        if chunks:
            output.write_bytes(b"".join(chunks))
            print(f"Saved event audio as WAV to {output} ({sum(map(len, chunks))} bytes)")
        else:
            print("No synthesis event audio was returned; verify voice/target compatibility.")
    finally:
        recognizer.synthesizing.disconnect_all()


if __name__ == "__main__":
    main()
