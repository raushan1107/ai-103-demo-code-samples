"""Shared setup for the M2 demos that use the Microsoft Agent Framework."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def required_setting(name: str) -> str:
    """Read a required setting and explain how to supply it."""
    value = os.getenv(name)
    if not value or value.startswith("YOUR-"):
        raise RuntimeError(f"Set {name} in the project-root .env file first.")
    return value


def foundry_chat_client():
    """Return a Foundry chat client authenticated with the signed-in Azure CLI user."""
    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential

    return FoundryChatClient(
        project_endpoint=required_setting("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"),
        model=required_setting("AZURE_AI_FOUNDRY_MODEL"),
        credential=AzureCliCredential(),   #az login must be run first
    )
