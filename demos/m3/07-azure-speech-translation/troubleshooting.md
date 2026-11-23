# Speech Translation troubleshooting

| Symptom / class | Diagnose | Fix |
|---|---|---|
| Authentication (401) | Confirm the resource key belongs to the Speech account. | Update `AZURE_SPEECH_KEY`; never paste it into source. |
| Authorization / forbidden | Check resource network restrictions and identity policy if using Entra auth. | Permit the client network or assign the supported Speech role. |
| Wrong region / endpoint | Verify the Speech account's region matches `AZURE_SPEECH_REGION`. | Use the account region, not a Translator or Foundry endpoint. |
| NoMatch | Check microphone selection, input level, source language and noise. | Allow microphone access; speak one short sentence in the configured language. |
| Canceled | Inspect `CancellationDetails.reason` and `error_details`. | Correct the reported auth, quota, region, or connection issue. |
| Target translation absent | Inspect `result.translations.keys()`. | Use a supported target language code and check request details. |
| Synthesized audio absent | Check the target voice and the synthesizing callback. | Match the voice locale to the target and request exactly one target for event mode. |
| Invalid voice | Confirm voice is supported in the Speech region and matches the language. | Use a voice listed for the chosen locale. |
| Throttling / quota | Inspect SDK cancellation and Azure metrics. | Reduce request rate or review quota; do not retry in a tight loop. |
| Device error | Run `python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"`. | Install PortAudio/PyAudio and check OS privacy controls and device contention. |

For generic portal “User tool error” messages, the text alone is insufficient. Capture timestamp, operation, request/correlation ID, resource region and detailed SDK/service error. Reproduce with the smallest independent script before testing the complete app. Never include keys or tokens in logs.
