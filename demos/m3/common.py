"""Shared M3 configuration helpers."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value or value.startswith("<") or value.startswith("YOUR-"):
        raise RuntimeError(f"Set {name} in the project-root .env file first.")
    return value
