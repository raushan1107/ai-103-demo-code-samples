"""Command-line startup diagnostics; no network requests or secret output."""

import json
import logging

from app.config import diagnostics

logger = logging.getLogger("globalcare.diagnostics")


def classify_error(error: Exception) -> dict[str, str]:
    """Summarize common service failures and safe request IDs, never headers/tokens."""
    status = getattr(error, "status_code", None)
    name = type(error).__name__.casefold()
    text = str(error).casefold()
    if status == 401 or "authentication" in name or "credential" in name:
        category = "Authentication failure"
    elif status == 403 or "authorization" in name:
        category = "Authorization/RBAC failure"
    elif status == 404:
        category = "Endpoint, project, agent or deployment not found"
    elif status == 429:
        category = "Quota or throttling"
    elif status == 400:
        category = "Invalid request, configuration or unsupported feature"
    elif isinstance(error, (ConnectionError, TimeoutError)):
        category = "Network or WebSocket failure"
    elif "audio" in text or "microphone" in text or "portaudio" in text:
        category = "Audio device failure"
    elif isinstance(error, ImportError):
        category = "Missing dependency"
    else:
        category = "Unclassified service/tool failure"
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", {}) or {}
    request_id = next((headers[key] for key in ("x-ms-request-id", "apim-request-id", "x-request-id") if key in headers), "")
    details = str(error)
    logger.error("classification=%s status=%s request_id=%s details=%s", category, status or "", request_id, details)
    result = {"classification": category, "details": details}
    if status is not None:
        result["http_status"] = str(status)
    if request_id:
        result["request_id"] = request_id
    return result

def main() -> None:
    print(json.dumps(diagnostics(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
