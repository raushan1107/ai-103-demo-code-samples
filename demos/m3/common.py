"""Shared M3 configuration helpers."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value or value.startswith("<") or value.startswith("YOUR-"):
        raise RuntimeError(f"Set {name} in the project-root .env file first.")
    return value


def configure_console_encoding() -> None:
    """Keep Hindi and other Unicode demo text usable in Windows terminals."""
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def foundry_client() -> tuple[OpenAI, str]:
    """Return an OpenAI client and deployment configured for Microsoft Foundry."""
    client = OpenAI(
        base_url=required_setting("AZURE_AI_FOUNDRY_ENDPOINT"),
        api_key=required_setting("AZURE_AI_FOUNDRY_API_KEY"),
    )
    return client, required_setting("AZURE_AI_FOUNDRY_MODEL")
