"""M1 demo: Endpoint configuration.

Run from the project root: python demos/m1/M1_15_endpoint_configuration.py
Shows how endpoint settings construct clients without sending a model request.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load the project .env regardless of the terminal's current working directory.
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def explain_client(label: str, endpoint_key: str, key_name: str, model_name: str) -> None:
    # Read the endpoint, credential, and deployment independently for clarity.
    endpoint = os.getenv(endpoint_key)
    api_key = os.getenv(key_name)
    model = os.getenv(model_name)
    if not endpoint or not api_key or not model or "YOUR-" in endpoint or "YOUR_" in model:
        print(f"{label}: configure {endpoint_key}, {key_name}, and {model_name} in .env")
        return
    # OpenAI is the Python SDK class; base_url routes requests to the chosen service.
    client = OpenAI(base_url=endpoint, api_key=api_key)
    print(f"{label}: ready for deployment {model} at {client.base_url}")


def main() -> None:
    explain_client("Foundry project API", "AZURE_AI_FOUNDRY_ENDPOINT", "AZURE_AI_FOUNDRY_API_KEY", "AZURE_AI_FOUNDRY_MODEL")
    explain_client("Azure OpenAI API", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_MODEL")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_15.
# Before running: configure Foundry settings; configure Azure OpenAI settings to show both.
# Command from the project root: python demos/m1/M1_15_endpoint_configuration.py; it makes no API request.

# Sample input and expected output for classroom demonstration:
# Sample input: none; this script does not prompt for input.
# Example output: which Foundry/Azure OpenAI client settings are ready, or which settings to configure; no API request is made.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_15_endpoint_configuration.py
# This is a configuration-only demo; it makes no model API request.
