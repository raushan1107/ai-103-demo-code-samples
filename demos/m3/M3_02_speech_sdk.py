"""Speech SDK text-to-audio, WAV transcription, and terminal voice conversation.

Run from the repository root:
    python demos/m3/M3_02_speech_sdk.py

Choose live conversation to speak into the default microphone and hear the
Foundry model's reply from the default speaker. That mode does not write audio
files. Choose save-audio mode when you want a WAV to keep or play later.
"""

from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

from common import ROOT, configure_console_encoding, foundry_client, required_setting

VOICE_NAME = "en-US-AriaNeural"


def speech_config() -> speechsdk.SpeechConfig:
    """Create a Speech configuration from the root .env key and region."""
    config = speechsdk.SpeechConfig(
        subscription=required_setting("AZURE_SPEECH_KEY"),
        region=required_setting("AZURE_SPEECH_REGION"),
    )
    config.speech_synthesis_voice_name = VOICE_NAME
    return config


def recognize_from_microphone(audio_path: str = "") -> str | None:
    """Recognize one microphone utterance or WAV turn; return None for no match."""
    if audio_path:
        path = Path(audio_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"WAV file not found: {path}")
        input_audio = speechsdk.audio.AudioConfig(filename=str(path))
    else:
        input_audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config(),
        audio_config=input_audio,
    )
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"You: {result.text}")
        return result.text
    if result.reason == speechsdk.ResultReason.NoMatch:
        print(f"No speech recognized: {result.no_match_details}")
        return None
    details = speechsdk.CancellationDetails.from_result(result)
    raise RuntimeError(
        f"Speech recognition canceled ({details.reason}): {details.error_details}"
    )


def speak_to_default_speaker(text: str) -> None:
    """Play synthesized text through the default speaker without saving a file."""
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config(),
        audio_config=speechsdk.audio.AudioOutputConfig(use_default_speaker=True),
    )
    result = synthesizer.speak_text_async(text).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(
            f"Speech synthesis canceled ({details.reason}): {details.error_details}"
        )


def live_conversation() -> None:
    """Run sequential microphone → Foundry response → speaker turns in the terminal."""
    model_client, model = foundry_client()
    history = []
    instructions = (
        "You are a friendly, concise voice assistant in a classroom demo. "
        "Answer the user's question clearly in a few short sentences."
    )
    print("Live voice conversation ready. Speak after each prompt; say 'quit' or 'exit' to end.")
    try:
        while True:
            source = input("\nPress Enter to speak, enter a WAV path, or type 'quit': ").strip().strip('"')
            if source.casefold() in {"quit", "exit", "stop"}:
                print("Assistant: Goodbye!")
                break
            if not source:
                print("Listening…")
            question = recognize_from_microphone(source)
            if question is None:
                continue
            if question.casefold().strip(" .!?'") in {"quit", "exit", "stop"}:
                print("Assistant: Goodbye!")
                break

            history.append({"role": "user", "content": question})
            response = model_client.responses.create(
                model=model,
                instructions=instructions,
                input=history,
                max_output_tokens=300,
            )
            history.extend(response.output)
            answer = response.output_text.strip()
            if not answer:
                print("Assistant returned no text for this turn. Try a shorter question.")
                continue
            print(f"Assistant: {answer}")
            speak_to_default_speaker(answer)
    finally:
        model_client.close()


def save_synthesized_audio() -> None:
    """Synthesize entered text into a WAV file for later playback."""
    text = input("Text to synthesize and save: ").strip()
    if not text:
        print("No text entered.")
        return

    output = ROOT / "sample_data" / "speech_output.wav"
    audio = speechsdk.audio.AudioOutputConfig(filename=str(output))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config(), audio_config=audio
    )
    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Saved speech to {output}")
    else:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(
            f"Speech synthesis canceled ({details.reason}): {details.error_details}"
        )


def transcribe_wav() -> None:
    """Recognize one utterance from a local WAV file."""
    audio_path = input("WAV file path: ").strip().strip('"')
    if not audio_path:
        print("No file path entered.")
        return
    path = Path(audio_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"WAV file not found: {path}")
    audio = speechsdk.audio.AudioConfig(filename=str(path))
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config(), audio_config=audio
    )
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Transcript: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print(f"No speech recognized: {result.no_match_details}")
    else:
        details = speechsdk.CancellationDetails.from_result(result)
        raise RuntimeError(
            f"Speech recognition canceled ({details.reason}): {details.error_details}"
        )


def main() -> None:
    configure_console_encoding()
    print("Azure Speech SDK options")
    print("1. Live voice conversation (microphone → Foundry model → speaker; no WAV saved)")
    print("2. Synthesize text and save a WAV file")
    print("3. Transcribe a WAV file")
    choice = input("Choose 1, 2, or 3 [1]: ").strip() or "1"
    if choice == "1":
        live_conversation()
    elif choice == "2":
        save_synthesized_audio()
    elif choice == "3":
        transcribe_wav()
    else:
        print("Choose 1, 2, or 3.")


if __name__ == "__main__":
    main()


# M3_02 WALKTHROUGH AND TEST
# Command from repository root:
#   python demos/m3/M3_02_speech_sdk.py
# Choice 1: use AZURE_SPEECH_* plus AZURE_AI_FOUNDRY_*; ask aloud:
#   What is the capital of France?
# For a repeatable test, enter sample_data/speech_output.wav at the audio-source
# prompt (it contains a harmless synthetic sentence); otherwise press Enter to
# use the microphone. The default speaker plays the model reply directly.
# Example question WAV: synthesize "What is the capital of France?" with option 2,
# then use that WAV in option 1. Expected: "You: What is the capital of France?"
# followed by a model answer such as "Assistant: The capital of France is Paris."
# The wording can vary. The answer is spoken; live mode does not save it as a WAV.
# Expected: a recognized transcript, a concise terminal response, then the
# response is spoken through the default speaker. Say "quit" to end. No audio
# file is generated in this mode. This is sequential Speech SDK + model turn-taking,
# not the bidirectional Voice Agent session in M3_08.
# Choice 2: enter "Hello, welcome to the speech demonstration." Expected:
#   sample_data/speech_output.wav is saved; open/play it manually if desired.
# Choice 3: enter a WAV path. Expected: "Transcript: ..." or a useful NoMatch.
# M3_02 is for synthetic, non-sensitive classroom questions only.
