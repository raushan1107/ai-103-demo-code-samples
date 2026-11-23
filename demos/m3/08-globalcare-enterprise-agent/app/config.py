"""Central configuration and non-secret diagnostics for GlobalCare."""

import importlib.metadata
import os
import shutil
import subprocess
import socket
from dataclasses import dataclass
from urllib.parse import urlparse
from packaging.version import Version

from dotenv import load_dotenv

load_dotenv()


def _setting(primary: str, fallback: str = "", default: str = "") -> str:
    """Prefer GlobalCare-specific configuration and reuse existing M3/M2 values."""
    value = os.getenv(primary, "")
    if value and not value.startswith(("YOUR-", "<")):
        return value
    value = os.getenv(fallback, "") if fallback else ""
    if value and not value.startswith(("YOUR-", "<")):
        return value
    return default


@dataclass(frozen=True)
class Settings:
    project_endpoint: str = _setting("GC_FOUNDRY_PROJECT_ENDPOINT", "AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
    model_endpoint: str = _setting("GC_FOUNDRY_MODEL_ENDPOINT", "AZURE_AI_FOUNDRY_ENDPOINT")
    model_key: str = _setting("GC_FOUNDRY_MODEL_KEY", "AZURE_AI_FOUNDRY_API_KEY")
    model_deployment: str = _setting("GC_FOUNDRY_MODEL_DEPLOYMENT", "AZURE_AI_FOUNDRY_MODEL")
    agent_name: str = os.getenv("GC_FOUNDRY_AGENT_NAME", "")
    language_endpoint: str = _setting("GC_LANGUAGE_ENDPOINT", "AZURE_LANGUAGE_ENDPOINT")
    language_key: str = _setting("GC_LANGUAGE_KEY", "AZURE_LANGUAGE_KEY")
    translator_endpoint: str = _setting("GC_TRANSLATOR_ENDPOINT", "AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com/")
    translator_key: str = _setting("GC_TRANSLATOR_KEY", "AZURE_TRANSLATOR_KEY")
    translator_region: str = _setting("GC_TRANSLATOR_REGION", "AZURE_TRANSLATOR_REGION")
    speech_key: str = _setting("GC_SPEECH_KEY", "AZURE_SPEECH_KEY")
    speech_region: str = _setting("GC_SPEECH_REGION", "AZURE_SPEECH_REGION")


def diagnostics() -> list[dict[str, str]]:
    """Report setting presence and package/CLI state without revealing values."""
    s = Settings()
    rows = [{"check": "Python", "status": "OK" if tuple(map(int, __import__('sys').version.split()[0].split('.')[:2])) >= (3, 10) else "ERROR", "detail": __import__('sys').version.split()[0]}]
    for name, value in vars(s).items():
        required = name not in {"model_key", "agent_name", "translator_endpoint", "model_endpoint", "language_endpoint", "language_key", "translator_key", "translator_region", "speech_key", "speech_region"}
        configured = bool(value and not value.startswith(("YOUR-", "<")))
        rows.append({"check": name, "status": "OK" if configured else ("OPTIONAL" if not required else "MISSING"), "detail": "configured" if configured else "not set or placeholder"})
    minimum_versions = {
        "azure-ai-projects":"2.11.0", "azure-identity":"1.17.0",
        "azure-ai-textanalytics":"5.3.0", "azure-ai-translation-text":"1.0.0",
        "azure-cognitiveservices-speech":"1.47.0", "streamlit":"1.40.0", "pyaudio":"0.2.14",
    }
    for package, minimum in minimum_versions.items():
        try:
            version = importlib.metadata.version(package)
            state = "installed" if Version(version) >= Version(minimum) else "UPGRADE NEEDED"
        except importlib.metadata.PackageNotFoundError:
            version, state = "missing", "MISSING"
        rows.append({"check": package, "status": state, "detail": f"{version} (minimum {minimum})"})
    rows.append({"check": "Azure CLI", "status": "OK" if shutil.which("az") else "MISSING", "detail": "available" if shutil.which("az") else "az not found"})
    if shutil.which("az"):
        try:
            identity = subprocess.run(["az", "account", "show", "--query", "user.name", "-o", "tsv"], capture_output=True, text=True, timeout=8, check=True).stdout.strip()
            rows.append({"check":"Azure CLI login", "status":"OK", "detail":identity or "signed in"})
        except (subprocess.SubprocessError, OSError):
            rows.append({"check":"Azure CLI login", "status":"NOT SIGNED IN", "detail":"run az login"})
    for label, url in (("Foundry project endpoint", s.project_endpoint), ("Foundry model endpoint", s.model_endpoint), ("Language endpoint", s.language_endpoint), ("Translator endpoint", s.translator_endpoint)):
        valid = not url or (urlparse(url).scheme == "https" and bool(urlparse(url).netloc))
        rows.append({"check": label, "status": "OK" if valid else "INVALID", "detail": "HTTPS endpoint format" if valid else "must be an https URL"})
        if url and valid:
            try:
                with socket.create_connection((urlparse(url).hostname, 443), timeout=2):
                    state, detail = "REACHABLE", "TCP 443 reachable (does not validate API/auth)"
            except OSError as exc:
                state, detail = "UNREACHABLE", f"TCP 443 check failed: {type(exc).__name__}"
            rows.append({"check": f"{label} network", "status": state, "detail": detail})
    return rows
