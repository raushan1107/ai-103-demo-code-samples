"""Shared configuration helpers for Speech translation examples."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def speech_settings() -> tuple[str, str]:
    """Return Speech key and region, with a setup hint when absent."""
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    if not key or key.startswith("YOUR-"):
        raise RuntimeError("Set AZURE_SPEECH_KEY in the repository-root .env.")
    if not region or region.startswith("YOUR-"):
        raise RuntimeError("Set AZURE_SPEECH_REGION in the repository-root .env.")
    return key, region


def audio_output(name: str) -> Path:
    """Return a safe output path in the example's audio directory."""
    folder = Path(__file__).parent / "audio"
    folder.mkdir(exist_ok=True)
    return folder / name
