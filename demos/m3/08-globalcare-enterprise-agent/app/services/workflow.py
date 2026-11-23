"""Optional multilingual request path joining Language, Translator and an agent."""

import json
from typing import Any

from app.agents.foundry_agent import respond as foundry_respond
from app.agents.tool_agent import respond as responses_respond
from app.config import Settings
from app.services.foundry_model import answer as model_answer
from app.services.language import analyze
from app.services.translation import translate
from app.tools.knowledge_base import KnowledgeBase


def run_integrated(
    question: str,
    settings: Settings,
    kb: KnowledgeBase,
    backend: str = "foundry",
    preferred_language: str = "",
) -> dict[str, Any]:
    """Analyze/redact, translate to English, answer from KB, and translate back."""
    analysis = analyze(question, settings)
    source = preferred_language.strip() or str(analysis["language"]["code"])
    safe_text = str(analysis["redacted_text"])
    english_text = safe_text
    stages: list[dict[str, Any]] = [{"stage":"language_analysis", "result":analysis}]
    if source != "en":
        english_text = translate(safe_text, ["en"], source, settings)[0]["text"]
        stages.append({"stage":"question_translation", "source":source, "target":"en", "text":english_text})

    if backend == "foundry":
        answer, tool_trace = foundry_respond(english_text, settings, kb)
    elif backend == "responses":
        answer, tool_trace = responses_respond(english_text, settings, kb)
    elif backend == "basic":
        context = json.dumps({"hospitals":kb.search_hospitals(english_text), "faqs":kb.search_faq(english_text), "departments":kb.departments}, ensure_ascii=False)
        answer, tool_trace = model_answer(english_text, context, settings), []
        stages.append({"stage":"context_injection", "detail":"Local JSON context inserted; no tool function executed."})
    else:
        raise ValueError("backend must be 'foundry', 'responses', or 'basic'.")
    stages.append({"stage":"grounded_agent_response", "text":answer, "tools":tool_trace})

    localized = answer
    if source != "en":
        localized = translate(answer, [source], "en", settings)[0]["text"]
        stages.append({"stage":"answer_translation", "source":"en", "target":source, "text":localized})
    return {"source_language":source, "answer":localized, "english_answer":answer, "stages":stages}
