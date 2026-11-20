"""Use Azure Speech SDK for text synthesis and optional file transcription."""

from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from common import ROOT, required_setting


def speech_config() -> speechsdk.SpeechConfig:
    config = speechsdk.SpeechConfig(
        subscription=required_setting("AZURE_SPEECH_KEY"),
        region=required_setting("AZURE_SPEECH_REGION"),
    )
    config.speech_synthesis_voice_name = "en-US-AriaNeural"
    return config


def main() -> None:
    text = input("Text to synthesize: ").strip()
    if text:
        output = ROOT / "sample_data" / "speech_output.wav"
        audio = speechsdk.audio.AudioOutputConfig(filename=str(output))
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config(), audio_config=audio)
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Saved speech to {output}")
        else:
            print(f"Speech synthesis did not complete: {result.reason}")

    audio_path = input("Optional WAV file to transcribe (Enter to skip): ").strip()
    if audio_path:
        path = Path(audio_path)
        audio = speechsdk.audio.AudioConfig(filename=str(path))
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config(), audio_config=audio)
        result = recognizer.recognize_once_async().get()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Transcript: {result.text}")
        else:
            print(f"No transcript returned: {result.reason}")


if __name__ == "__main__":
    main()


# M3_02 WALKTHROUGH AND TEST
# 1. speech_config() builds the Speech client from the endpoint and key in .env.
# 2. The first prompt synthesizes text to sample_data/speech_output.wav.
# 3. The second prompt optionally recognizes one local WAV file; Enter skips it.
# From the repository root run:
#   python demos/m3/M3_02_speech_sdk.py
# Enter: Hello, welcome to the speech demonstration.
# Then press Enter to skip transcription, or provide a short WAV file path.
# Expected: sample_data/speech_output.wav is created and its path is printed;
# for a WAV input, a Transcript line contains the recognized words.
