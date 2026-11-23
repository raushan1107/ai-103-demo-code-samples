# Module 3 demo run guide

This guide follows `AI-103-03.pptx`. It supplies client-side demonstrations for Azure Language, Azure Speech, Azure Language/Speech MCP tools, Voice Live, and translation. Portal provisioning and costs depend on the tenant and region; do those steps before running a client. Run commands from the project root in the VS Code terminal.

## 1. Install packages and configure `.env`

Create/activate `.venv` and install `requirements.txt`. Sign in with `az login` for the Speech agent example. These M3 examples use Azure AI Language/Speech resource keys as shown in the slides; the local Language assistant and spoken-question assistant also use the M1 Foundry endpoint, API key, and model settings.

Add only the settings needed for the example:

```text
AZURE_LANGUAGE_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=<resource-key>
AZURE_SPEECH_ENDPOINT=https://<region>.api.cognitive.microsoft.com/
AZURE_SPEECH_KEY=<resource-key>
AZURE_SPEECH_REGION=<region>
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_KEY=<resource-key>
AZURE_TRANSLATOR_REGION=<region>
FOUNDRY_SPEECH_AGENT_NAME=<saved-speech-agent-name>
AZURE_SPEECH_MCP_STORAGE_SAS_URL=<container-sas-url>
```

For Language, use the Language account endpoint and key. For Speech, use the endpoint and region shown by the Speech resource (the endpoint is regional). For Translator, use the global text endpoint shown above and the Translator resource key and region. Keep `.env` local and secret. Do not place key values in slides, source files, or screenshots. The Foundry project endpoint/model used by M2 agent demos are in `guides/M2_DEMOS_RUN_GUIDE.md`.

For these classroom services, choose the **F0** free tier: Azure Language includes 5,000 text records/month, Speech includes up to 5 audio hours for speech recognition and speech translation plus 500,000 neural synthesis characters/month, and Translator includes 2 million translated characters/month. Requests beyond free quotas are not included; do not change these accounts to a paid SKU for this exercise. Foundry model tokens and unrelated M2 resources are billed separately, so keep model tests short and check your subscription's cost view.

For this workspace, the F0 accounts are `ai103-raushanranjan-lang-50209338`, `ai103-raushanranjan-speech-50209338`, and `ai103-raushanranjan-translator-50209338` in `rg-azure-ai-raushanranjan` (Australia East). Their endpoints, keys, and regions are configured in the Git-ignored `.env`; no secrets belong in this guide. The existing S0 AI Services account was left unchanged.

## 2. Language analysis (slides 4–8)

Provision/enable Azure Language in Foundry Tools and configure `AZURE_LANGUAGE_*`. Run:

```powershell
python demos/m3/M3_01_language_analysis.py
```

Enter sample text. The demo reports detected language, named entities, and PII categories. Use synthetic text only. The example detects PII; it does not modify or redact submitted text. For publishing workflows, review the detected spans and apply a separately tested redaction step.

## 3. Local Language tool-calling assistant (slides 9–13)

This example creates its assistant in the local Python process; it does not create or connect to a saved Foundry agent. The model runs through the M1 Foundry OpenAI-compatible endpoint, while function tools in the script call Azure AI Language for language detection, named entity extraction, and PII detection.

Configure `AZURE_AI_FOUNDRY_ENDPOINT`, `AZURE_AI_FOUNDRY_API_KEY`, and `AZURE_AI_FOUNDRY_MODEL` as in the M1 guide, plus `AZURE_LANGUAGE_ENDPOINT` and `AZURE_LANGUAGE_KEY`. Run from the project root:

```powershell
python demos/m3/M3_03_local_language_agent.py
```

Ask a question containing synthetic names, organizations, places, or contact details. Watch the local tool calls and the assistant's summary, then type `quit`. PII results sent back to the model include redacted text and categories, not the detected PII values. The user message itself is sent to the configured model, so use synthetic text only.

## 4. Speech synthesis and transcription (slides 14–18)

Provision Azure Speech and configure `AZURE_SPEECH_KEY`/`AZURE_SPEECH_REGION`. Live conversation also needs the M1 Foundry endpoint, key and deployment in `.env`, plus a working microphone and speaker. Run from the repository root:

```powershell
python demos/m3/M3_02_speech_sdk.py
```

Choose one of three terminal options:

1. **Live voice conversation:** press Enter at the prompt, then ask aloud, “What is the capital of France?” The terminal prints the recognized question and model response (for example, “The capital of France is Paris”); the response plays immediately through the default speaker. Say “quit” to end. For a repeatable test, synthesize that question with option 2, then enter `sample_data/speech_output.wav` at the live-mode input prompt. This sequential Speech SDK → Foundry model → Speech SDK flow writes no reply audio file.
2. **Save synthesized audio:** enter `Hello, welcome to the speech demonstration.` The script saves `sample_data/speech_output.wav` for later playback.
3. **Transcribe a WAV:** enter a local WAV path and read the transcript or NoMatch result.

Use synthetic, non-sensitive questions. The live mode is a turn-by-turn terminal voice assistant; M3_08 is the separate bidirectional Foundry Voice Agent realtime demo.

## 5. Foundry Speech SDK and Speech MCP agent (slides 19–31)

The SDK demo supports speech-to-text and text-to-speech. The MCP workflow additionally requires a storage container with a write SAS URL because the service saves generated audio there.

1. Create/open a Foundry project and deploy a compatible model.
2. Create an Azure Storage account and a private blob container for this classroom exercise.
3. Create a short-lived container SAS with the minimum permissions required by the current MCP setup guide. Store the SAS URL in `.env` as `AZURE_SPEECH_MCP_STORAGE_SAS_URL`; do not commit or share it.
4. In **Agents**, create a prompt agent and add the Azure Speech MCP server following [Azure Speech MCP](https://aka.ms/mslearn-speech-mcp). Provide the Speech resource endpoint/key and the container SAS URL in their designated connection fields.
5. Add instructions explaining when to transcribe a provided audio URL and when to synthesize text. Save and test the agent in the playground.
6. Set `FOUNDRY_SPEECH_AGENT_NAME` in `.env` to the saved agent name.
7. Run `python demos/m3/M3_04_connect_speech_agent.py`. Use a publicly accessible test audio URL only if the configured MCP tool accepts URLs; then request a short synthesized phrase.
8. Delete generated test blobs and revoke the SAS after the exercise. Remove only the classroom resources created for this lab.

The Microsoft MCP setup page controls the currently supported connection fields, URL, and SAS permission scope. Follow that page if its UI differs from these labels.

## 6. Voice Live agent (slides 32–36)

Voice Live is event-based and needs a compatible Foundry project, saved **voice-mode** agent, microphone/speaker, and a client. This repository includes that client in [M3_08 GlobalCare](../demos/m3/08-globalcare-enterprise-agent/README.md); it uses Entra ID and the current Azure AI Projects Voice Agent realtime SDK. Create and test the voice-mode agent in Foundry first. The M3_02 terminal conversation is a separate turn-by-turn Speech SDK + model example.

## 7. Text and speech translation (slides 37–43)

Configure Translator endpoint/key/region for text translation. Configure Speech endpoint/key/region for speech translation and prepare a short WAV sample. Run:

```powershell
python demos/m3/M3_05_translation.py
```

The script demonstrates text translate/transliterate and one-target-language speech translation. For speech synthesis of multiple target languages, use the returned translated text with text-to-speech separately; event-based synthesis is limited to one target language.

## 8. English/Hindi spoken question assistant

This end-to-end exercise combines Speech, Language, Translator, and a Foundry LLM. It listens to one short question from the default microphone in English or Hindi (or a WAV file for repeatable tests), detects the spoken and text language, translates the question to English, extracts entities and PII, sends the PII-redacted English text to the LLM, translates the answer back when needed, and synthesizes a WAV answer using an English or Hindi voice.

Configure `AZURE_SPEECH_*`, `AZURE_LANGUAGE_*`, and `AZURE_TRANSLATOR_*` as described above. Also configure the M1 Foundry OpenAI-compatible settings `AZURE_AI_FOUNDRY_ENDPOINT`, `AZURE_AI_FOUNDRY_API_KEY`, and `AZURE_AI_FOUNDRY_MODEL`; the project endpoint used by M2 is not a substitute. Allow microphone access and run from the project root:

```powershell
python demos/m3/M3_06_speech_language_llm.py
```

Ask a short question, for example “Who won the Under-19 Asia Cup in 2026?” or “2026 में अंडर-19 एशिया कप किसने जीता?” Press Enter at the WAV prompt to use the microphone, or supply a WAV path for a repeatable test. The model may not have current results; the prompt asks it to acknowledge when it is unsure. The exercise prints each pipeline stage, sends the PII-redacted English text to the model, and saves the spoken answer to `sample_data/speech_answer.wav` for playback. Use synthetic questions, since entity detection output can include the recognized entity text. Speech input is one turn per run.

## Speech translation lab (M3_07)

The independent scripts under `demos/m3/07-azure-speech-translation/` demonstrate microphone speech-to-text translation, single-target event-based synthesis, and manual speech synthesis for multiple target languages. Install its `requirements.txt`, set `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` in the root `.env`, then run each script from the repository root. See the [M3_07 trainer guide](../demos/m3/07-azure-speech-translation/README.md) for the classroom sequence, audio behavior, and troubleshooting.

## GlobalCare enterprise lab (M3_08)

The [GlobalCare AI lab](../demos/m3/08-globalcare-enterprise-agent/README.md) combines synthetic hospital data, Foundry tool calling, Language, Translator, Speech, and a saved Foundry voice agent. Install its separate requirements and launch Streamlit from the repository root. Run its offline tests from the M3_08 folder. Voice Live requires a configured **voice-mode** agent, project Entra ID permissions, and microphone/speaker access; text agents are not interchangeable.

## Cleanup and troubleshooting

- Do not use real personal data in demos. Azure Language PII detection is not guaranteed to identify every sensitive span.
- Check that Language uses its account endpoint, Speech uses its regional API endpoint, and Translator uses the global text endpoint; Speech and Translator also require the matching region.
- For authentication errors, check key/region pairing, resource deployment, network access, and project permissions.
- MCP agent setup can fail if its project connection, resource key, or storage SAS is invalid or expired. Recreate credentials from the portal and update local `.env`.
- Check current SDK/API requirements before class; service model names, endpoints, and portal forms can change.
