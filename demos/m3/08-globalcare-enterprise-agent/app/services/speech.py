"""File-based speech translation and synthesis for the Streamlit workflow."""

import tempfile
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from app.config import Settings

VOICES = {"en":"en-US-AriaNeural", "hi":"hi-IN-SwaraNeural", "fr":"fr-FR-DeniseNeural", "ja":"ja-JP-NanamiNeural"}


def translate_audio(path: str | Path, source: str, targets: list[str], settings: Settings) -> dict[str, object]:
    """Translate one uploaded WAV file to each selected target text language."""
    if not settings.speech_key or not settings.speech_region:
        raise RuntimeError("Configure AZURE_SPEECH_KEY and AZURE_SPEECH_REGION (or GC_SPEECH_*).")
    if not targets:
        raise ValueError("Select at least one target language.")
    config = speechsdk.translation.SpeechTranslationConfig(subscription=settings.speech_key, region=settings.speech_region)
    config.speech_recognition_language = source
    for target in targets:
        config.add_target_language(target)
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=config,
        audio_config=speechsdk.audio.AudioConfig(filename=str(path)),
    )
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError(f"NoMatch: {result.no_match_details}")
    if result.reason != speechsdk.ResultReason.TranslatedSpeech:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(f"Speech translation canceled: {details.reason}; {details.error_details}")
    return {"transcript": result.text, "translations": {language: result.translations.get(language, "") for language in targets}}


def synthesize(text: str, language: str, settings: Settings, voice: str = "") -> bytes:
    """Synthesize one translated text result and return a local WAV payload."""
    if not settings.speech_key or not settings.speech_region:
        raise RuntimeError("Configure AZURE_SPEECH_KEY and AZURE_SPEECH_REGION (or GC_SPEECH_*).")
    selected_voice = voice or VOICES.get(language)
    if not selected_voice:
        raise ValueError(f"Provide a supported neural voice for target language {language}.")
    config = speechsdk.SpeechConfig(subscription=settings.speech_key, region=settings.speech_region)
    config.speech_synthesis_voice_name = selected_voice
    output_path = ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output:
            output_path = output.name
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=config,
            audio_config=speechsdk.audio.AudioOutputConfig(filename=output_path),
        )
        result = synthesizer.speak_text_async(text).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            details = speechsdk.CancellationDetails.from_result(result)
            raise RuntimeError(f"Speech synthesis failed: {details.error_details or details.reason}")
        return Path(output_path).read_bytes()
    finally:
        if output_path:
            Path(output_path).unlink(missing_ok=True)
