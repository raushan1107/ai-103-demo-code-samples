# Module 3 demo run guide

This guide follows `AI-103-03.pptx`. It supplies client-side demonstrations for Azure Language, Azure Speech, Azure Language/Speech MCP tools, Voice Live, and translation. Portal provisioning and costs depend on the tenant and region; do those steps before running a client. Run commands from the project root in the VS Code terminal.

## 1. Install packages and configure `.env`

Create/activate `.venv` and install `requirements.txt`. Sign in with `az login` for Entra-authenticated samples. These M3 examples use Azure AI Language/Speech resource keys as shown in the slides, except the agent/client examples which use the existing M2 Foundry project and Entra setup.

Add only the settings needed for the example:

```text
AZURE_LANGUAGE_ENDPOINT=https://<resource>.services.ai.azure.com/
AZURE_LANGUAGE_KEY=<resource-key>
AZURE_SPEECH_ENDPOINT=https://<resource>.services.ai.azure.com/
AZURE_SPEECH_KEY=<resource-key>
AZURE_SPEECH_REGION=<resource-region>
AZURE_TRANSLATOR_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
AZURE_TRANSLATOR_KEY=<resource-key>
AZURE_TRANSLATOR_REGION=<resource-region>
FOUNDRY_LANGUAGE_AGENT_NAME=<saved-language-agent-name>
FOUNDRY_SPEECH_AGENT_NAME=<saved-speech-agent-name>
AZURE_SPEECH_MCP_STORAGE_SAS_URL=<container-sas-url>
```

In Microsoft Foundry, open the Language/Speech resource's **Keys and Endpoint** page. Copy the endpoint and a key there; use the resource's region for SDKs that request a region. Keep `.env` local and secret. Do not place key values in slides, source files, or screenshots. The Foundry project endpoint/model used for MCP agent demos are the M2 settings in `guides/M2_DEMOS_RUN_GUIDE.md`.

## 2. Language analysis (slides 4–8)

Provision/enable Azure Language in Foundry Tools and configure `AZURE_LANGUAGE_*`. Run:

```powershell
python demos/m3/M3_01_language_analysis.py
```

Enter sample text. The demo reports detected language, named entities, and PII categories. Use synthetic text only. The example detects PII; it does not modify or redact submitted text. For publishing workflows, review the detected spans and apply a separately tested redaction step.

## 3. Language MCP agent (slides 9–13)

Create a Foundry project and model deployment and set `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` and `AZURE_AI_FOUNDRY_MODEL`. In the project portal:

1. Open **Agents** and create a prompt agent using the deployed model.
2. Add the Azure Language MCP server using the endpoint and authentication method shown by the current Azure Language MCP instructions: [Azure Language MCP](https://aka.ms/mslearn-language-mcp).
3. If the connection form asks for an endpoint/key, use the Language resource values in `.env`; do not paste them into the agent instructions.
4. Add instructions to use language detection, entity extraction, and PII detection only when relevant, and to report tool errors clearly.
5. Save, open the playground, and test with fictional text containing a name, organization, place, email, and phone number. Confirm the agent selects the relevant MCP tools and explains results.
6. Copy the saved agent's name to `FOUNDRY_LANGUAGE_AGENT_NAME` in `.env`.
7. Run `python demos/m3/M3_03_connect_language_agent.py`; ask another synthetic-text question and then type `quit`.

Portal labels, authentication fields, and server URLs can change. Use the linked Microsoft setup instructions as the source of the current MCP endpoint and supported auth options; the client code only connects to the saved agent.

## 4. Speech synthesis and transcription (slides 14–18)

Provision Azure Speech, copy endpoint/key/region, and prepare a short, non-sensitive WAV file. Run:

```powershell
python demos/m3/M3_02_speech_sdk.py
```

Enter a sentence for synthesis, then enter the path to a WAV file for transcription (press Enter to skip transcription). Synthesis writes `sample_data/speech_output.wav`; transcription uses one-shot recognition and may return no match for long audio. Confirm the selected region and supported audio format before class.

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

Voice Live is event-based and needs a compatible resource/model, microphone and speaker, and a client implementation. In the Foundry agent playground, enable **Audio mode**, configure **Voice Live**, and test a short turn. The deck describes the client lifecycle: connect, configure audio devices, start a session, process events, and handle interruption events. This repository does not yet include a Voice Live client; use the linked [Voice Live agent exercise](https://aka.ms/mslearn-voice-live-agent) for its supported SDK and event details.

## 7. Text and speech translation (slides 37–43)

Configure Translator endpoint/key/region for text translation. Configure Speech endpoint/key/region for speech translation and prepare a short WAV sample. Run:

```powershell
python demos/m3/M3_05_translation.py
```

The script demonstrates text translate/transliterate and one-target-language speech translation. For speech synthesis of multiple target languages, use the returned translated text with text-to-speech separately; event-based synthesis is limited to one target language.

## Cleanup and troubleshooting

- Do not use real personal data in demos. Azure Language PII detection is not guaranteed to identify every sensitive span.
- Check endpoint family carefully: Language/Speech use the `services.ai.azure.com` resource endpoint; Translator may use a `cognitiveservices.azure.com` endpoint.
- For authentication errors, check key/region pairing, resource deployment, network access, and project permissions.
- MCP agent setup can fail if its project connection, resource key, or storage SAS is invalid or expired. Recreate credentials from the portal and update local `.env`.
- Check current SDK/API requirements before class; service model names, endpoints, and portal forms can change.
