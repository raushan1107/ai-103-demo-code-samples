"""Streamlit training UI for the fictional GlobalCare administrative assistant."""

import json
import logging
import sys
import tempfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agents.tool_agent import respond
from app.agents.foundry_agent import respond as respond_with_foundry_agent
from app.config import Settings, diagnostics
from app.diagnostics import classify_error
from app.services.language import analyze
from app.services.foundry_model import answer as answer_with_model
from app.services.translation import supported_languages, translate, transliterate
from app.services.workflow import run_integrated
from app.services.speech import synthesize, translate_audio
from app.services.voice_live import run as voice_run
from app.tools.knowledge_base import KnowledgeBase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
st.set_page_config(page_title="GlobalCare AI | M3 Lab", page_icon="🌐", layout="wide")
st.title("GlobalCare AI · Module 3 training lab")
st.caption("Fictional administrative information only. Not a medical diagnosis or treatment system.")
settings = Settings()
kb = KnowledgeBase()


def show_error(error: Exception) -> None:
    """Show a classified error and available request ID without exposing credentials."""
    summary = classify_error(error)
    st.error(f"{summary['classification']}: {summary['details']}")
    if "request_id" in summary:
        st.caption(f"Request ID: {summary['request_id']}")


section = st.sidebar.radio("Lab section", ["Dashboard", "Text assistant", "Integrated workflow", "Knowledge explorer", "Language analysis", "Text translation", "Speech translation", "Voice Live", "Execution logs", "Configuration and diagnostics"])

if section == "Dashboard":
    st.subheader("Multilingual reception workflow")
    st.markdown("Use the verified synthetic hospital data, analyze text with Language, translate with Translator, and optionally connect a saved Foundry voice agent.")
    st.metric("Synthetic hospitals", len(kb.hospitals))
    st.metric("Hospital FAQ records", len(kb.faqs))
    st.info("The tool-calling assistant uses an OpenAI-compatible Foundry model. Local JSON tools are the source of factual hospital details.")
elif section == "Text assistant":
    question = st.text_area("Reception request", "What are the reception hours at CityCare Hospital in Bengaluru?")
    backend = st.selectbox("Implementation", ["Foundry Agent Service (Entra ID)", "Module 1 Responses function calling (API key)", "Module 1 basic grounded response (no tools)"])
    if st.button("Ask GlobalCare"):
        with st.spinner("Calling Foundry and verified knowledge tools…"):
            try:
                if backend.startswith("Foundry"):
                    response, trace = respond_with_foundry_agent(question, settings, kb)
                elif backend.startswith("Module 1 Responses"):
                    response, trace = respond(question, settings, kb)
                else:
                    # Module 1 context insertion: deterministic local records enter the prompt;
                    # this path intentionally makes no tool call.
                    context = json.dumps({
                        "hospitals": kb.search_hospitals(question),
                        "faqs": kb.search_faq(question),
                        "departments": kb.departments,
                        "services": kb.services,
                    }, ensure_ascii=False)
                    response, trace = answer_with_model(question, context, settings), []
                    st.caption("This Module 1 path inserted locally selected JSON context; no function tools ran.")
                st.session_state["last_trace"] = trace
                st.markdown(response)
                st.json(trace)
            except Exception as exc: show_error(exc)
elif section == "Integrated workflow":
    question = st.text_area("Synthetic reception request", "My name is Asha Rao. I need an appointment at CityCare Hospital in Bengaluru.")
    preferred = st.text_input("Preferred language code (blank = detected)", "")
    backend_name = st.selectbox("Agent backend", ["Foundry Agent Service", "M1 Responses function calling", "M1 basic context response"])
    backend_key = {"Foundry Agent Service":"foundry", "M1 Responses function calling":"responses", "M1 basic context response":"basic"}[backend_name]
    if st.button("Run full text workflow"):
        try:
            result = run_integrated(question, settings, kb, backend_key, preferred)
            st.markdown(result["answer"])
            st.subheader("Pipeline stages")
            st.json(result["stages"])
            st.session_state["last_trace"] = [tool for stage in result["stages"] for tool in stage.get("tools", [])]
        except Exception as exc: show_error(exc)
elif section == "Knowledge explorer":
    for hospital in kb.hospitals:
        with st.expander(f"{hospital['name']} · {hospital['city']}"):
            st.json(hospital)
            st.write("Hours", kb.get_opening_hours(hospital["id"]))
            st.write("Languages", kb.get_supported_languages(hospital["id"]))
elif section == "Language analysis":
    text = st.text_area("Synthetic sample", "My name is Asha Rao. I need an appointment at CityCare Hospital in Bengaluru.")
    if st.button("Analyze text"):
        try: st.json(analyze(text, settings))
        except Exception as exc: show_error(exc)
elif section == "Text translation":
    text = st.text_area("Text", "こんにちは。予約をお願いします。")
    source = st.text_input("Source language (optional)", "ja") or None
    targets = st.text_input("Target languages, comma separated", "en,hi")
    if st.button("Translate"):
        try: st.json(translate(text, [part.strip() for part in targets.split(",") if part.strip()], source, settings))
        except Exception as exc: show_error(exc)
    text_script = st.text_input("Japanese text to transliterate", "こんにちは")
    if st.button("Transliterate Japanese to Latin"):
        try: st.write(transliterate(text_script, "ja", "Jpan", "Latn", settings))
        except Exception as exc: show_error(exc)
    if st.button("Fetch supported capabilities"):
        try: st.session_state["translator_languages"] = supported_languages(settings)
        except Exception as exc: show_error(exc)
    catalog = st.session_state.get("translator_languages")
    if catalog:
        translation_codes = catalog["translation"]
        transliteration_codes = catalog["transliteration"]
        codes = sorted(set(translation_codes) | set(transliteration_codes))
        st.dataframe([{
            "code": code,
            "language": (translation_codes.get(code) or transliteration_codes.get(code) or {}).get("name", ""),
            "translation": code in translation_codes,
            "transliteration": code in transliteration_codes,
        } for code in codes], use_container_width=True)
elif section == "Speech translation":
    st.write("Upload a short WAV for translated text and optional speech output. For live microphone and event-based single-target exercises, use the terminal scripts linked below.")
    uploaded = st.file_uploader("Short WAV audio", type=["wav"])
    source = st.text_input("Source speech locale", "en-US")
    targets = st.text_input("Target language codes", "hi,fr")
    make_speech = st.checkbox("Synthesize each target translation")
    if st.button("Translate speech file"):
        if not uploaded:
            st.warning("Upload a WAV file first.")
        else:
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as input_file:
                    input_file.write(uploaded.getvalue())
                    wav_path = input_file.name
                try:
                    result = translate_audio(wav_path, source, [code.strip() for code in targets.split(",") if code.strip()], settings)
                finally:
                    Path(wav_path).unlink(missing_ok=True)
                st.write("Transcript:", result["transcript"])
                for language, text in result["translations"].items():
                    st.write(f"{language}: {text}")
                    if make_speech and text:
                        st.audio(synthesize(text, language, settings), format="audio/wav")
            except Exception as exc: show_error(exc)
    st.code("python demos/m3/07-azure-speech-translation/speech_to_text_translation.py\npython demos/m3/07-azure-speech-translation/event_based_synthesis.py\npython demos/m3/07-azure-speech-translation/manual_synthesis.py", language="powershell")
elif section == "Voice Live":
    st.warning("Requires a saved voice-mode Foundry agent; text agents are not interchangeable with voice agents.")
    if st.button("Start Voice Live session"):
        try: voice_run()
        except Exception as exc: show_error(exc)
elif section == "Execution logs":
    st.json(st.session_state.get("last_trace", []))
    st.caption("Trace records include tool name, arguments and actual local result. No tool call is claimed unless it ran.")
else:
    st.write("Checks show presence and format only; secrets are never displayed.")
    st.dataframe(diagnostics(), use_container_width=True)
    st.info("Grant the signed-in identity Foundry User on the project for agent invocation. Language, Speech and Translator resource keys are scoped to their respective endpoints and must never be exposed in browser code.")
