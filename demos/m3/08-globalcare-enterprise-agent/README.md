# M3_08 · GlobalCare AI enterprise training lab

## 1–3. Learning objective, problem and concepts

Build a small multilingual administrative reception assistant. It combines Module 1 response generation, Module 2 function/tool calling and Module 3 Language, Translator, Speech and Foundry realtime voice. All hospital and contact data is fictional. This is **not** a diagnosis or treatment system.

The JSON reference data is the factual source of truth. Tools read that data; the model turns actual results into a concise answer. Empty results remain empty, and instructions require the agent to disclose missing information.

## 4. Architecture

See [architecture.md](architecture.md) for service boundaries and tool sequence diagrams. Core components:

- `data/`: fictional hospitals, departments, services, FAQs and language catalog.
- `app/tools/knowledge_base.py`: six read-only local lookup functions.
- `app/agents/foundry_agent.py`: temporary Foundry Agent Service prompt agent with Python function tools, using Entra ID; cleans up its conversation and version.
- `app/agents/tool_agent.py`: M1 OpenAI-compatible Responses API function-calling variant, using its API key.
- `app/services/`: independent Language, Translator, model and Voice Agent clients.
- `app/main.py`: Streamlit training interface.
- `app/diagnostics.py`: local non-secret configuration diagnostics.
- `tests/`: offline knowledge-base and mocked Translator configuration tests.

## 5–9. Azure resources, prerequisites, authentication, SDKs

Python 3.10+ is required. Foundry agent and Voice Live paths require a Foundry project, a supported model/voice configuration, Azure CLI login and **Foundry User** (or equivalent permissions to create and invoke agents) on that project. The Voice Live section additionally requires a saved voice-mode Foundry agent and voice-agent feature/region access. For the M1 mode, configure an OpenAI-compatible Foundry endpoint, key and deployment. Language, Translator and Speech examples need their corresponding Azure resources and endpoint/key/region values.

Before Voice Live: open the intended Foundry project in the portal, confirm voice-agent availability for its region/subscription, build a new agent with **Interaction mode: Voice**, choose an available model/voice, set administrative-only instructions, save, and test the microphone in the playground. Assign the signed-in identity **Foundry User** on the project (or an equivalent least-privilege role). Put the exact voice-agent name and project endpoint in `.env`. A saved text-mode agent cannot be converted; create a separate voice-mode agent.

Microsoft Learn recommends `azure-ai-projects[voice]>=2.11.0` for current Python voice-agent sessions. This Foundry voice-agent API currently has preview aspects; check region/feature availability. The integration uses `AzureCliCredential`, not an API key. Direct service Voice Live API keys and Foundry voice-agent invocation are distinct auth routes; this demo chooses the Foundry agent route and Entra ID. Endpoint types are not interchangeable.

**Realtime audio concepts.** The session is an event-driven, bidirectional WebSocket managed by the SDK. The lifecycle is connect → capture/send → receive server events → stop/close audio and session. The microphone and speaker use 24 kHz, mono, signed PCM16 in this example. PCM16 is uncompressed linear audio; G.711 μ-law and A-law are companded 8 kHz telephony formats. μ-law is common in North American/Japanese telephony and A-law is common in many other telephony networks; neither is a drop-in substitute for PCM16 without a compatible negotiated format or conversion. Sample rate and channel count must match the stream contract. The agent/service may provide server-side turn detection and noise reduction according to its saved configuration; use a headset to reduce acoustic echo. Voice settings such as model, voice, turn detection, input/output formats and available noise reduction are part of the saved voice-agent configuration. This Python client uses the Foundry project endpoint and saved voice-agent name. Standalone Voice Live resource connections use a separate Voice Live endpoint and can support resource-key or Entra auth, but those credentials do not replace Entra ID for the Foundry agent integration. This UI must run on the machine with the microphone/speaker; it does not expose credentials to browser JavaScript. Avatar rendering and browser WebRTC transport are separate client implementations and are not included here.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r demos/m3/08-globalcare-enterprise-agent/requirements.txt
az login
```

Copy [`.env.example`](.env.example) placeholders into the repository root `.env`, then set only values needed by your chosen UI sections. M3_08 does not print secret values.

| Variable group | Used for | Authentication |
|---|---|---|
| `GC_FOUNDRY_PROJECT_ENDPOINT`, `GC_FOUNDRY_MODEL_DEPLOYMENT` | Foundry Agent Service and Voice Agent | Entra ID via `az login` |
| `GC_FOUNDRY_MODEL_ENDPOINT`, `GC_FOUNDRY_MODEL_KEY` | M1 Responses modes | OpenAI-compatible resource key |
| `GC_LANGUAGE_ENDPOINT`, `GC_LANGUAGE_KEY` | Detection, NER and PII | Language resource key |
| `GC_TRANSLATOR_ENDPOINT`, `GC_TRANSLATOR_KEY`, `GC_TRANSLATOR_REGION` | Text translation and transliteration | Translator resource key and region |
| `GC_SPEECH_KEY`, `GC_SPEECH_REGION` | WAV speech translation and synthesis | Speech resource key and region |
| `GC_FOUNDRY_VOICE_AGENT_NAME` | Voice Live session | Existing voice-mode agent name; Entra ID |

When a `GC_*` service value is unset, the app reuses corresponding existing `AZURE_*` values from the repository `.env` for M1/M3 services. The voice-agent name must still be set explicitly.

## 10–12. Code walkthrough and run

From the repository root:

```powershell
Push-Location demos/m3/08-globalcare-enterprise-agent
python -m unittest discover -s tests -v
python -m app.diagnostics
Pop-Location
streamlit run demos/m3/08-globalcare-enterprise-agent/app/main.py
```

The app sections are Dashboard, Text assistant, Integrated workflow, Knowledge explorer, Language analysis, Text translation, Speech translation, Voice Live, Execution logs, and Configuration/diagnostics. The Integrated workflow analyzes and redacts input, translates to English when needed, invokes the selected grounded agent, then translates the answer back. In Text assistant select either the temporary Foundry Agent Service path or the M1 Responses function-calling path. The first path creates a temporary tool-enabled agent, logs each executed tool and cleans up. The UI is server-side Python; keys and Entra tokens do not go to browser JavaScript.

The Streamlit Speech translation page accepts a short WAV upload and can synthesize each target. The independent [M3_07](../07-azure-speech-translation/README.md) scripts support either microphone or WAV input and include event-based single-target synthesis. Voice Live requires `GC_FOUNDRY_VOICE_AGENT_NAME` to name an existing voice-mode agent. No simulation is substituted when it is absent.

Expected KB examples: search Bengaluru returns CityCare Hospital; unknown hospital IDs return no record; reception hours appear exactly as stored. Cloud answers depend on configured credentials, model/deployment, region and service availability.

## 13. Classroom demonstration script

1. Open Dashboard and state that the data is fabricated and the assistant is administrative only.
2. Open Knowledge Explorer; show the source records before asking the agent.
3. Ask “What are reception hours at CityCare Hospital in Bengaluru?” Select Foundry Agent Service and inspect the function-call trace.
4. Ask for a hospital not present. Confirm the response admits the data is unavailable; inspect the empty result.
5. Enter the sample Asha request in Language Analysis. Show language, entity categories and redacted text; PII values are not returned in the structured result.
6. Translate Japanese text to English and Hindi. Explain language codes and one request with multiple targets.
7. Run M3_07 event synthesis with one target, then manual synthesis with two targets.
8. Start Voice Live only after the saved voice agent is configured; speak a short administrative question and interrupt a spoken response.

## 14. Questions and student exercises

- Why should verified facts come from tools rather than model memory?
- Which values belong in the project endpoint, model endpoint, Speech region and Translator endpoint?
- Exercise: add a fictional hospital, add its reception department, test the knowledge tool, and verify the UI can return those hours.
- Exercise: configure English-to-Hindi translation, then Japanese kana-to-Latin transliteration. Explain why the results are different operations.
- Expected: local tests pass; KB lookup returns exact new fixture values; service calls require configured credentials.

## 15–16. Common errors and troubleshooting

See [troubleshooting.md](troubleshooting.md). Run diagnostics before cloud calls. A “User tool error” alone does not identify the failing component; inspect full Foundry traces/errors, correlation IDs and separately test endpoint, auth, agent, tool and downstream service.

## 17. Security considerations

Use synthetic data only. Do not enter real patient details. Store secrets in ignored root `.env`, rotate leaked keys, use least privilege, and prefer Entra ID for Foundry. The Voice Agent may store conversation artifacts depending on its saved configuration; verify retention and disable storage where appropriate. Logs contain synthetic tool arguments/results and must not be extended to include sensitive inputs.

## 18. Limitations

This is an instructional prototype. It has no patient identity verification, appointment transaction system, emergency routing, clinical knowledge, uptime target or production privacy controls. The included datasets are deliberately small. Model answers can still be wrong despite grounding, so verify consequential details against the source.

Voice Agent APIs/features and Speech/Translator language coverage change over time; validate feature availability in the target region. Voice Live needs microphone/speaker access and a saved voice agent. The script streams mono PCM16 at 24 kHz. G.711 μ-law and A-law are telephony codecs and are not the PCM format used by this sample. Noise suppression, turn detection and echo cancellation support depends on the server-side agent configuration and audio hardware. Avatar rendering/WebRTC is not implemented; it is a separate client integration.

## 19. AI-103 takeaways

Separate language-specific NLP (detection, NER, PII) from generative responses; recognize when to use translation, transliteration, speech recognition, synthesis, and realtime agents; distinguish Entra ID from resource key authentication; ground enterprise responses in approved data; treat tool schemas, logs, privacy, RBAC, region and endpoint selection as design requirements.

## 20. Official references

- [Create a voice-based prompt agent](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-voice-agent)
- [Use hosted agents with a voice agent](https://learn.microsoft.com/azure/foundry/how-to/voice-first-with-hosted-agent)
- [Migrate Voice Live integration to Foundry voice agents](https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-from-voice-live)
- [TextTranslationClient Python reference](https://learn.microsoft.com/python/api/azure-ai-translation-text/azure.ai.translation.text.texttranslationclient)
- [Speech translation for Python](https://learn.microsoft.com/azure/ai-services/speech-service/how-to-translate-speech?pivots=programming-language-python)
