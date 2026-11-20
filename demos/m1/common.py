"""Shared, explained setup for the M1 demonstration scripts."""
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Resolve project root so dotenv works when launched from the root or VS Code.
ROOT = Path(__file__).resolve().parents[2]
# Load settings from the local .env file while preserving OS-provided overrides.
load_dotenv(ROOT / ".env")


def required_setting(name: str) -> str:
    """Read a setting or give the learner an actionable setup message."""
    import os
    value = os.getenv(name)
    if not value or value.startswith("YOUR-") or value == "YOUR_API_KEY":
        raise RuntimeError(f"Missing {name}; copy .env.example to .env and configure it.")
    return value


def foundry_client() -> tuple[OpenAI, str]:
    """Return OpenAI SDK client and Foundry deployment for the project endpoint."""
    endpoint = required_setting("AZURE_AI_FOUNDRY_ENDPOINT")
    api_key = required_setting("AZURE_AI_FOUNDRY_API_KEY")
    model = required_setting("AZURE_AI_FOUNDRY_MODEL")
    # Use OpenAI SDK with Foundry's compatible URL; model is the deployment name.
    return OpenAI(base_url=endpoint, api_key=api_key), model



