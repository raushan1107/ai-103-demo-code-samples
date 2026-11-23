# GlobalCare troubleshooting and diagnostic guide

Run `python -m app.diagnostics` from this directory or use the UI's Configuration page. It reports setting presence, package versions, CLI availability/login, and HTTPS endpoint shape. It never prints keys or tokens. Endpoint reachability is not proof of valid authentication, region support, model availability, or RBAC.

| Failure class | Meaning and safe reproduction | Diagnose and fix | Check in Foundry / Azure |
|---|---|---|---|
| Authentication | `az login` missing or key invalid. | Run `az account show`; rotate and update only the affected resource key. | Confirm tenant/subscription and resource key. |
| Authorization/RBAC | Identity authenticated but role lacks invoke/create. | Check project role assignment; grant least privilege. | Foundry User on project for agent create/invoke and Voice Agent calls. |
| Incorrect endpoint | Request reaches the wrong API host/path. | Compare endpoint type and URL format in `.env`; don't interchange project/model/Speech/Translator endpoints. | Copy project endpoint from project Overview and service endpoints from resource. |
| Incorrect project ID | Project path resolves to no project. | Compare endpoint's `/api/projects/<project>` with Foundry project Overview. | Confirm selected account/project and tenant. |
| Agent name/version | Agent not found or incompatible text-vs-voice agent. | Check exact saved name/version and interaction mode. | Verify the agent is voice-mode for Voice Live; a prompt text agent won't work. |
| Model deployment unavailable | Model is missing, region unsupported, or quota is insufficient. | Verify exact deployment and current region/model availability. | Model deployments and quota in the intended project. |
| Unsupported region | Selected model/voice/API not offered in region. | Check current service availability before retrying. | Compare resource region with regional feature matrix. |
| SDK mismatch | Missing method/event or unexpected object type. | Compare installed package against this lab's lower bounds; use a clean venv. | Use current Learn sample/version and refresh package metadata. |
| WebSocket failure | Realtime route blocked, proxy issue, or token rejected. | Check `HTTPS_PROXY`, network egress, endpoint, Entra token and correlation ID. | Project firewall, region support, Voice Agent feature. |
| Audio device | PyAudio cannot open microphone/speaker. | Check device count, OS privacy, sample format, 24-kHz mono PCM16. Use headset. | Not usually a portal failure. |
| Microphone permission | OS denied capture. | Allow desktop Python/terminal access, then retry. | N/A |
| Missing dependency | ImportError / missing audio runtime. | `pip install -r requirements.txt`; install PortAudio as OS requires. | N/A |
| Quota / throttling | Service rejected rate/usage. | Reduce calls, inspect retry-after and quota metrics. | Quota, SKU and region in Azure portal. |
| Tool invocation failure | Agent requested invalid arguments, tool errored, or no tool call occurred. | Review the execution trace, schema, JSON arguments and result; replay a local KB call. | Agent instructions/model tool list; no claim of execution if trace is empty. |
| Knowledge lookup failure | Tool returns empty data or JSON fails to load. | Verify synthetic JSON and hospital ID in `data/`; unknown records intentionally return empty/None. | N/A |
| Generic “User tool error” | Portal displays a wrapper message that hides the underlying operation. | The message alone is insufficient. Isolate project auth, agent invocation, tool and resource calls; capture full service error, timestamp and request/correlation ID. | Agent trace/logs, project connection, permissions and configured tool details. |

Never log `.env`, keys, SAS URLs or bearer tokens. Synthetic health-adjacent sample text only. Keep generated transcripts/audio local and delete them after class.
