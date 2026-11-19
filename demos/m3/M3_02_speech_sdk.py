"""Use Azure Speech SDK for text synthesis and optional file transcription."""

from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from common import ROOT, required_setting


def speech_config() -> speechsdk.SpeechConfig:
    config = speechsdk.SpeechConfig(
        subscription=required_setting("AZURE_SPEECH_KEY"),
        endpoint=required_setting("AZURE_SPEECH_ENDPOINT"),
    )
    config.speech_synthesis_voice_name = "en-US-AriaNeural"
    return config


def main() -> None:
    text = input("Text to synthesize: ").strip()
    if text:
        output = ROOT / "sample_data" / "speech_output.wav"
        audio = speechsdk.audio.AudioOutputConfig(filename=str(output))
        result = speechsdk.SpeechSynthesizer(speech_config=speech_config(), audio_config=audio).speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Saved speech to {output}")
        else:
            print(f"Speech synthesis did not complete: {result.reason}")

    audio_path = input("Optional WAV file to transcribe (Enter to skip): ").strip()
    if audio_path:
        path = Path(audio_path)
        audio = speechsdk.audio.AudioConfig(filename=str(path))
        result = speechsdk.SpeechRecognizer(speech_config=speech_config(), audio_config=audio).recognize_once_async().get()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Transcript: {result.text}")
        else:
            print(f"No transcript returned: {result.reason}")


if __name__ == "__main__":
    main()
