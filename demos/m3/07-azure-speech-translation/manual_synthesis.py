"""Translate microphone speech to several languages and synthesize each separately."""

import azure.cognitiveservices.speech as speechsdk
from pathlib import Path

from speech_config import audio_output, speech_settings

VOICES = {"hi": "hi-IN-SwaraNeural", "fr": "fr-FR-DeniseNeural", "ja": "ja-JP-NanamiNeural"}


def main() -> None:
    key, region = speech_settings()
    source = input("Source speech language [en-US]: ").strip() or "en-US"
    targets = input("Target language codes [hi,fr]: ").strip() or "hi,fr"
    languages = [item.strip() for item in targets.split(",") if item.strip()]
    if not languages:
        raise ValueError("Enter at least one target language code.")
    config = speechsdk.translation.SpeechTranslationConfig(subscription=key, region=region)
    config.speech_recognition_language = source
    for language in languages:
        config.add_target_language(language)
    source_audio = input("Optional WAV file (Enter to use microphone): ").strip()
    audio_config = (speechsdk.audio.AudioConfig(filename=str(Path(source_audio))) if source_audio
                    else speechsdk.audio.AudioConfig(use_default_microphone=True))
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=config,
        audio_config=audio_config,
    )
    print("Speak one short sentence." if not source_audio else f"Reading {source_audio}")
    result = recognizer.recognize_once_async().get()
    if result.reason != speechsdk.ResultReason.TranslatedSpeech:
        if result.reason == speechsdk.ResultReason.NoMatch:
            print(f"NoMatch: {result.no_match_details}")
            return
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(f"Speech translation canceled: {details.reason}; {details.error_details}")
    print(f"Transcript: {result.text}")
    for language in languages:
        text = result.translations.get(language)
        if not text:
            print(f"No translation returned for {language}; skipping synthesis.")
            continue
        voice = VOICES.get(language) or input(f"Neural voice name for {language}: ").strip()
        config_out = speechsdk.SpeechConfig(subscription=key, region=region)
        config_out.speech_synthesis_voice_name = voice
        path = audio_output(f"manual-{language}.wav")
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=config_out,
            audio_config=speechsdk.audio.AudioOutputConfig(filename=str(path)),
        )
        synthesis = synthesizer.speak_text_async(text).get()
        if synthesis.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            details = speechsdk.CancellationDetails.from_result(synthesis)
            raise RuntimeError(f"Synthesis failed for {language}: {details.error_details or details.reason}")
        print(f"{language}: {text}\nSaved: {path}")


if __name__ == "__main__":
    main()
