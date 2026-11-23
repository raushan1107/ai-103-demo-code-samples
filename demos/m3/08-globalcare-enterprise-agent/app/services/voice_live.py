"""Hands-free microphone client for a saved Microsoft Foundry voice agent."""

import asyncio
import base64
import os
import queue
import threading
from typing import Any

from dotenv import load_dotenv
from app.config import Settings

load_dotenv()
SAMPLE_RATE = 24000
CHUNK_SAMPLES = 1200


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Set {name} in the project-root .env. Create a voice-mode Foundry agent first.")
    return value


def run() -> None:
    """Connect via the official Foundry Voice Agent realtime SDK and stream PCM16 audio."""
    asyncio.run(_run())


async def _run() -> None:
    try:
        import pyaudio
        from azure.ai.projects.aio import AIProjectClient
        from azure.ai.projects.models import RealtimeServerEventType
        from azure.identity.aio import AzureCliCredential
    except ImportError as exc:
        raise RuntimeError("Install the enterprise requirements, including azure-ai-projects[voice] and pyaudio.") from exc

    endpoint = Settings().project_endpoint or _required("GC_FOUNDRY_PROJECT_ENDPOINT")
    agent = _required("GC_FOUNDRY_VOICE_AGENT_NAME")
    credential = AzureCliCredential()
    audio = pyaudio.PyAudio()
    incoming: queue.Queue[bytes] = queue.Queue(maxsize=40)
    playback: queue.Queue[bytes | None] = queue.Queue(maxsize=80)
    speaker_remaining = bytearray()
    stop = threading.Event()
    loop = asyncio.get_running_loop()
    input_stream = None
    output_stream = None

    def microphone_callback(data: bytes, _frames: int, _time: Any, _status: Any) -> tuple[None, int]:
        try:
            incoming.put_nowait(data)
        except queue.Full:
            pass  # Bound latency by dropping an old frame rather than growing memory.
        return None, pyaudio.paContinue

    def speaker_callback(_data: Any, frames: int, _time: Any, _status: Any) -> tuple[bytes, int]:
        nonlocal speaker_remaining
        expected = frames * 2  # mono, 16-bit PCM
        while len(speaker_remaining) < expected:
            try:
                chunk = playback.get_nowait()
            except queue.Empty:
                break
            if chunk:
                speaker_remaining.extend(chunk)
        output = bytes(speaker_remaining[:expected])
        del speaker_remaining[:expected]
        return output.ljust(expected, b"\0"), pyaudio.paContinue

    try:
        input_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True,
                                  frames_per_buffer=CHUNK_SAMPLES, stream_callback=microphone_callback)
        output_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True,
                                   frames_per_buffer=CHUNK_SAMPLES, stream_callback=speaker_callback)
        async with credential:
            async with AIProjectClient(endpoint=endpoint, credential=credential) as project:
                async with project.beta.voice_agents.realtime.connect(agent_name=agent) as connection:
                    input_stream.start_stream()
                    output_stream.start_stream()
                    print("Connected. Speak naturally; interrupt the agent to test barge-in. Ctrl+C ends the session.")

                    async def send_audio() -> None:
                        while not stop.is_set():
                            try:
                                pcm = await asyncio.to_thread(incoming.get, True, 0.1)
                            except queue.Empty:
                                continue
                            await connection.input_audio_buffer.append(audio=pcm)

                    sender = asyncio.create_task(send_audio())
                    try:
                        async for event in connection:
                            kind = getattr(event, "type", "")
                            if kind == RealtimeServerEventType.SESSION_CREATED:
                                print("Realtime session created by Foundry.")
                            elif kind == RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                                speaker_remaining.clear()
                                while not playback.empty():
                                    try: playback.get_nowait()
                                    except queue.Empty: break
                                print("[listening]")
                            elif kind == RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                                print(f"You: {getattr(event, 'transcript', '')}")
                            elif kind == RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA:
                                delta = getattr(event, "delta", b"")
                                if isinstance(delta, str): delta = base64.b64decode(delta)
                                try: playback.put_nowait(delta)
                                except queue.Full: pass
                            elif kind == RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE:
                                print(f"Agent: {getattr(event, 'transcript', '')}")
                            elif kind == RealtimeServerEventType.RESPONSE_DONE:
                                response = getattr(event, "response", None)
                                status = getattr(response, "status", "unknown")
                                if status not in {"completed", "unknown"}:
                                    print(f"Agent response ended with status: {status}")
                            elif kind == RealtimeServerEventType.ERROR:
                                error = getattr(event, "error", None)
                                raise RuntimeError(f"Voice session error: {getattr(error, 'message', error)}")
                    finally:
                        stop.set()
                        sender.cancel()
                        await asyncio.gather(sender, return_exceptions=True)
    except KeyboardInterrupt:
        print("\nVoice session ended by user.")
    except Exception as exc:
        raise RuntimeError(f"Foundry voice session failed; check agent, project endpoint, region and Foundry User role: {exc}") from exc
    finally:
        stop.set()
        if input_stream is not None:
            if input_stream.is_active(): input_stream.stop_stream()
            input_stream.close()
        if output_stream is not None:
            if output_stream.is_active(): output_stream.stop_stream()
            output_stream.close()
        audio.terminate()
