# Module 3 · Language, Speech, Translation and Voice

This folder extends the existing six numbered M3 Python demos. It keeps the root repository `.env` and `requirements.txt` conventions and adds two practical labs:

| Demo | Focus | Run |
|---|---|---|
| M3_01–M3_06 | Language, terminal voice conversation and WAV synthesis/transcription, local Language assistant, saved Speech agent, translation, spoken question assistant | [M3 run guide](../../guides/M3_DEMOS_RUN_GUIDE.md) |
| M3_07 | Speech-to-text translation, single-target event synthesis, multi-target manual synthesis | [M3_07 README](07-azure-speech-translation/README.md) |
| M3_08 | GlobalCare multilingual enterprise lab: Foundry tools, Language, Translator, Speech, Voice Agent and Streamlit | [M3_08 README](08-globalcare-enterprise-agent/README.md) |

Install repository dependencies from the root with `python -m pip install -r requirements.txt`. M3_08 has additional dependencies in its own requirements file. Copy only placeholders from [M3 .env template](.env.example) into your ignored root `.env` and fill values for the exercise being run.

The Voice Live SDK path in M3_08 uses the current Foundry voice-agent integration in `azure-ai-projects[voice]` and requires a saved **voice-mode** agent plus Microsoft Entra ID. Existing Foundry text agents are not interchangeable with voice agents. No live voice service is simulated.
