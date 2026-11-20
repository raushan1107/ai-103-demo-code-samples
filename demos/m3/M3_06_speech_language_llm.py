"""Speak in English or Hindi; detect, translate, analyze, answer, and speak back."""

import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.translation.text import TextTranslationClient
from azure.ai.translation.text.models import InputTextItem
from azure.core.credentials import AzureKeyCredential

from common import ROOT, configure_console_encoding, foundry_client, required_setting


def recognize_question(
    audio_config: speechsdk.audio.AudioConfig,
    subscription: str,
    region: str,
) -> tuple[str, str]:
    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-US", "hi-IN"]
    )
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        auto_detect_source_language_config=auto_detect,
    )
    result = recognizer.recognize_once_async().get()
    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(
            f"Speech recognition failed ({result.reason}): "
            f"{details.error_details or details.reason}"
        )
    language = speechsdk.AutoDetectSourceLanguageResult(result).language
    return result.text, language


def main() -> None:
    configure_console_encoding()
    speech_key = required_setting("AZURE_SPEECH_KEY")
    speech_region = required_setting("AZURE_SPEECH_REGION")
    language_client = TextAnalyticsClient(
        endpoint=required_setting("AZURE_LANGUAGE_ENDPOINT"),
        credential=AzureKeyCredential(required_setting("AZURE_LANGUAGE_KEY")),
    )
    translator = TextTranslationClient(
        endpoint=required_setting("AZURE_TRANSLATOR_ENDPOINT"),
        credential=AzureKeyCredential(required_setting("AZURE_TRANSLATOR_KEY")),
        region=required_setting("AZURE_TRANSLATOR_REGION"),
    )
    llm, model = foundry_client()

    print("Ask a short question in English or Hindi.")
    audio_path = input("WAV file for a repeatable test (Enter to use microphone): ").strip()
    audio_config = (
        speechsdk.audio.AudioConfig(filename=audio_path)
        if audio_path
        else speechsdk.audio.AudioConfig(use_default_microphone=True)
    )
    if not audio_path:
        print("Speak after the prompt.")
    question, speech_language = recognize_question(
        audio_config,
        subscription=speech_key,
        region=speech_region,
    )
    print(f"\nSpeech detected: {speech_language}")
    print(f"Transcript: {question}")

    detected = language_client.detect_language([question])[0]
    if detected.is_error:
        raise RuntimeError(f"Language detection failed: {detected.error}")
    language_code = detected.primary_language.iso6391_name
    print(f"Text language: {detected.primary_language.name} ({language_code})")

    translation = translator.translate(
        body=[InputTextItem(text=question)], to_language=["en"]
    )[0]
    english_question = translation.translations[0].text
    print(f"English translation: {english_question}")

    entities_result = language_client.recognize_entities([english_question])[0]
    if entities_result.is_error:
        raise RuntimeError(f"Entity extraction failed: {entities_result.error}")
    print("Entities:")
    if entities_result.entities:
        for entity in entities_result.entities:
            print(f"- {entity.text}: {entity.category}")
    else:
        print("- None found")

    pii_result = language_client.recognize_pii_entities([english_question])[0]
    if pii_result.is_error:
        raise RuntimeError(f"PII detection failed: {pii_result.error}")
    print(f"PII detected: {len(pii_result.entities)} item(s)")
    for pii_entity in pii_result.entities:
        print(f"- {pii_entity.category}")
    print("The LLM receives the PII-redacted question.")

    response = llm.responses.create(
        model=model,
        instructions=(
            "Answer the user's question clearly in English. If you are unsure or "
            "the question needs current information, say so instead of guessing."
        ),
        input=pii_result.redacted_text,
    )
    english_answer = response.output_text
    print(f"\nLLM answer (English): {english_answer}")

    if language_code != "en":
        answer_translation = translator.translate(
            body=[InputTextItem(text=english_answer)],
            from_language="en",
            to_language=[language_code],
        )[0]
        spoken_answer = answer_translation.translations[0].text
    else:
        spoken_answer = english_answer
    print(f"Answer in your language: {spoken_answer}")

    voice = "hi-IN-SwaraNeural" if language_code == "hi" else "en-US-AriaNeural"
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=speech_region,
    )
    speech_config.speech_synthesis_voice_name = voice
    output = ROOT / "sample_data" / "speech_answer.wav"
    audio = speechsdk.audio.AudioOutputConfig(filename=str(output))
    synthesis = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio,
    )
    synthesis_result = synthesis.speak_text_async(spoken_answer).get()
    if synthesis_result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = speechsdk.CancellationDetails.from_result(synthesis_result)
        raise RuntimeError(
            f"Speech synthesis failed ({synthesis_result.reason}): "
            f"{details.error_details or details.reason}"
        )
    print(f"Saved spoken answer to {output}")


if __name__ == "__main__":
    main()


# M3_06 WALKTHROUGH AND TEST
# 1. The setup creates Speech, Language, Translator, and Foundry clients from .env.
# 2. Speech recognizes one microphone turn (or a provided WAV file for testing)
#    and auto-detects English or Hindi.
# 3. Azure Language confirms the transcript's language; Translator converts the
#    question to English; Language then extracts entities and detects PII.
# 4. Foundry answers the PII-redacted English question. Translator converts the
#    answer back when needed, and Speech saves audio using the matching voice.
#    Play sample_data/speech_answer.wav to hear the response.
#    Use synthetic speech only; the model deployment may have separate token costs.
#
# From the repository root run:
#   python demos/m3/M3_06_speech_language_llm.py
# Say: Who won the Under-19 Asia Cup in 2026?
# Or say in Hindi: 2026 mein under-19 Asia Cup kisne jeeta?
# For a repeatable file test, provide a WAV path at the input prompt; press Enter
# to use the microphone.
# Expected: detected language, transcript, English translation, entities/PII,
# English model answer, answer translation when needed, and a WAV speech answer. The
# model may not know current tournament results and should say when uncertain.
