# AI-103 Demo Code Samples

<p align="center">
  <strong>Hands-on Python demos for Microsoft Azure AI and Microsoft Foundry</strong><br>
  <em>Learn by running, inspecting, and adapting small examples.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10 or later">
  <img src="https://img.shields.io/badge/Azure-AI-0078D4?logo=microsoftazure&logoColor=white" alt="Microsoft Azure AI">
  <img src="https://img.shields.io/badge/Modules-1%20to%203-6C5CE7" alt="Modules 1 to 3">
</p>

> **Maintained by Raushan Ranjan (MCT)**
>
> This repository is a growing collection. New modules and demos can be added over time.

## What you'll find here

This repository contains runnable examples that accompany AI-103 training:

| Module | Topics | Examples |
| --- | --- | ---: |
| **M1 — Model APIs and application patterns** | Responses, conversations, prompting, hosted tools, function calling, RAG, evaluation, fine-tuning concepts, responsible AI | 15 |
| **M2 — Agents and workflows** | Microsoft Agent Framework, function tools, MCP, Foundry IQ retrieval, sequential agents | 8 |
| **M3 — Language, speech, and translation** | Azure AI Language, Speech, Language/Speech agents, text and speech translation | 5 |

The examples are designed for learning and demonstration, not production deployment. They keep core calls visible and explain where portal setup, credentials, permissions, or human review are required.

## Quick start

### 1. Prerequisites

- Python **3.10 or later**
- Git
- A Microsoft Azure account and access to the Azure AI resources used by the demos you choose
- Azure CLI for Entra-authenticated examples in M2 and some M3 demos

Azure resource creation and model deployments are not automated by this repository. Service availability, permissions, and charges depend on your Azure subscription and region.

### 2. Clone the repository

```powershell
git clone https://github.com/raushan1107/ai-103-demo-code-samples.git
cd ai-103-demo-code-samples
```

### 3. Create and activate a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

Run this from the repository root:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configure credentials

Create your private local environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace placeholders for the demos you plan to run. The file is intentionally ignored by Git; **never commit real keys, SAS URLs, or tokens**.

| Module | Configuration |
| --- | --- |
| **M1** | Foundry OpenAI-compatible endpoint, API key, and exact model deployment name. M1_15 can also use Azure OpenAI settings. |
| **M2** | Foundry project endpoint and model deployment; sign in with `az login`. M2_06 additionally needs the knowledge-base MCP endpoint and its project connection ID. M2_08 needs the name of an existing prompt agent. |
| **M3** | Azure AI Language, Speech, and Translator endpoints/keys/regions as needed. Agent demos also need an existing Foundry project and saved agent names. The Speech MCP demo may need a container SAS URL. |

**Important:** M1 uses an OpenAI-compatible endpoint and API key. M2 uses a Foundry **project endpoint** and Entra ID via Azure CLI; do not substitute the M1 endpoint. For M2:

```powershell
az login
```

Check each module's run guide for exact portal setup, permissions, supported models, and required settings:

- [M1 demo run guide](guides/M1_DEMOS_RUN_GUIDE.md)
- [M2 demo run guide](guides/M2_DEMOS_RUN_GUIDE.md)
- [M3 demo run guide](guides/M3_DEMOS_RUN_GUIDE.md)

## Run a demo

Run commands from the repository root with the virtual environment active. For example:

```powershell
python demos/m1/M1_01_first_response.py
python demos/m2/M2_01_first_agent.py
python demos/m3/M3_01_language_analysis.py
```

Each script's name identifies its module and sequence number. Read the script comments and the matching run guide before the demo; some examples require portal setup or interactive input.

### Module 1 — Model APIs and application patterns

Start with [M1_01_first_response.py](demos/m1/M1_01_first_response.py). The full set includes conversation state, Chat Completions, prompt engineering, Code Interpreter, web and file search, function calling, local RAG, model comparison, evaluation, a fine-tuned model evaluation example, responsible AI review, an expense-assistant capstone, and endpoint configuration.

- [M1 run guide](guides/M1_DEMOS_RUN_GUIDE.md)
- [Sample prompts and outputs](guides/M1_DEMO_SAMPLE_INPUTS_AND_OUTPUTS.md)
- [Fine-tuning student lab](guides/M1_12_FINETUNING_STUDENT_LAB.md)

The fine-tuning demo evaluates an already deployed model; it does not create a fine-tuning job.

### Module 2 — Agents and workflows

Start with [M2_01_first_agent.py](demos/m2/M2_01_first_agent.py). Continue through Python tools, Foundry function calling, local MCP, Foundry IQ retrieval, sequential agents, and connecting to a portal-created agent.

- [M2 run guide](guides/M2_DEMOS_RUN_GUIDE.md)
- [Agent build and workflow guide](guides/M2_AGENT_BUILD_AND_WORKFLOW_GUIDE.md)
- [Sample prompts and outputs](guides/M2_DEMO_SAMPLE_INPUTS_AND_OUTPUTS.md)

Some examples create temporary Foundry agents or conversations and attempt cleanup when they finish. M2_06 requires an existing Foundry IQ knowledge base, a correctly configured project connection, and Search access for the Foundry project identity.

### Module 3 — Language, speech, and translation

Start with [M3_01_language_analysis.py](demos/m3/M3_01_language_analysis.py). The set also includes Speech synthesis/transcription, clients for portal-created Language and Speech agents, and text/speech translation.

- [M3 run guide](guides/M3_DEMOS_RUN_GUIDE.md)

Voice Live is covered as a portal/exercise walkthrough in the guide; this repository does not currently include a local Voice Live client.

## Repository layout

```text
demos/
  m1/                 Model API and application-pattern demos
  m2/                 Agent, tool, MCP, and workflow demos
  m3/                 Language, speech, and translation demos
guides/                Setup, run instructions, and teaching material
sample_data/           Non-sensitive demo policy and fine-tuning examples
.env.example           Safe template for local configuration
requirements.txt       Python dependencies for all current modules
```

## Data, safety, and cost

- Use synthetic or otherwise approved data. Do not send personal, confidential, or regulated information to a demo service.
- The included expense policy and fine-tuning data are classroom samples.
- Model requests and hosted tools may incur Azure charges. Review pricing and quotas before running a demo.
- Some scripts create temporary service-side resources. Check their cleanup behavior and verify cleanup in the portal if a run is interrupted.
- A model response is not a substitute for human review, especially for safety, privacy, financial, or consequential decisions.

## Troubleshooting

- **Missing Python package:** Activate `.venv`, then run `python -m pip install -r requirements.txt`.
- **Missing setting:** Confirm `.env` is in the repository root and that the selected demo's required values have been filled in.
- **401 / 403:** Check the selected Azure identity, endpoint/key pairing, project role, resource network rules, and any managed-identity role assignments described in the module guide.
- **Deployment not found:** Use the exact deployment name shown in Foundry, not only the model family name.
- **Unsupported tool or API:** Verify the model, region, endpoint, and API version support the requested tool.
- **MCP or Foundry IQ error:** Confirm the MCP URL is the knowledge-base endpoint, the project connection targets that endpoint, the knowledge source is indexed, and the Foundry identity has the required Search data role.

## Extending the collection

When adding a future module or demo:

1. Put runnable scripts under `demos/mN/` and use consistent numbered names.
2. Keep reusable module setup in that module's `common.py`.
3. Add prerequisites, configuration names, run commands, and troubleshooting notes to a matching guide under `guides/`.
4. Add only non-sensitive sample data that the code actually uses.
5. Update this README's module table and links so learners can find the new material.

---

<p align="center">
  <strong>Happy learning!</strong><br>
  <strong>Raushan Ranjan (MCT)</strong>
</p>
