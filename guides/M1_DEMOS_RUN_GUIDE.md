# Module 1 demo run guide

This guide gives the preparation and portal steps that are easy to miss when reading only a run command in a Python file. The slide deck is the available lesson source; the referenced handbook folder was not found in the project or under `R:\Demos`.

## One-time workstation setup

1. Install Python 3.10 or later and Visual Studio Code.
2. Open `R:\Demos\AI-103` in VS Code.
3. Create a virtual environment in the integrated terminal:
   - Windows: `py -m venv .venv`
   - PowerShell: `\.venv\Scripts\Activate.ps1`
   - Command Prompt: `.venv\Scripts\activate.bat`
4. Install packages: `python -m pip install -r requirements.txt`.
5. Copy `.env.example` to `.env` in the project root.
6. In the Microsoft Foundry portal, choose the appropriate project and deployed model, then copy its OpenAI-compatible endpoint and key to `.env` as `AZURE_AI_FOUNDRY_ENDPOINT`, `AZURE_AI_FOUNDRY_API_KEY`, and `AZURE_AI_FOUNDRY_MODEL`. The model value must be the deployment name shown in Foundry.
7. Keep `.env` secret. Do not paste keys into source files, screenshots, or class materials.
8. Run demos from the project root so commands and sample paths match the examples.

Basic smoke demonstration: `python demos/m1/M1_01_first_response.py`. It should print a model-generated answer. This sends a billable request to the configured deployment.

## Per-demo preparation and steps

### M1_01_first_response.py — first Responses API call

**Portal first:** Create/open a Foundry project, deploy a model that supports the Responses API, and put its endpoint, key, and deployment name in `.env`.

**Run:** `python demos/m1/M1_01_first_response.py`

**Show:** Point to `OpenAI(...)` setup in `demos/m1/common.py`, then `client.responses.create(...)`, the deployment name passed as `model`, and `response.output_text`.

### M1_02_responses_conversation.py — Responses conversation state

**Portal first:** Same Foundry project and compatible deployment as M1_01.

**Run:** `python demos/m1/M1_02_responses_conversation.py`; ask a follow-up that depends on an earlier answer, then type `quit`.

**Show:** `previous_response_id` starts as `None`, is sent on each request, then is updated from `response.id`.

### M1_03_chat_completions_history.py — Chat Completions history

**Portal first:** Same project; choose a deployment that supports Chat Completions.

**Run:** `python demos/m1/M1_03_chat_completions_history.py`; ask a question and a contextual follow-up, then type `quit`.

**Show:** The app appends each user and assistant turn to `messages`, resending the conversation on the next API call.

### M1_04_prompt_engineering.py — system prompt and few-shot examples

**Portal first:** Same project and a deployment supporting Responses API. No data upload is needed.

**Run:** `python demos/m1/M1_04_prompt_engineering.py`; ask a Python question, then optionally ask an unrelated question to show scope instructions.

**Show:** System instructions, two examples, a requested output structure, and the sampling temperature. Prompting shapes one request; it does not train the model.

### M1_05_tool_code_interpreter.py — hosted Code Interpreter

**Portal first:** Confirm that the selected deployment, API version, region, and project support Responses API Code Interpreter. Some deployment combinations do not expose this hosted tool. Confirm classroom billing policy.

**Run:** `python demos/m1/M1_05_tool_code_interpreter.py`.

**Show:** `tools` enables the hosted sandbox. The Python code runs in the service-managed container, not in the local VS Code Python process. If the API says the tool is unsupported, use a compatible deployment or skip this example.

### M1_06_tool_web_search.py — hosted web search

**Portal first:** Confirm deployment and region support the Responses API `web_search` tool and that outbound/current search is permitted for the project. Confirm billing policy.

**Run:** `python demos/m1/M1_06_tool_web_search.py`.

**Show:** The request asks for current information and provides `web_search` as an available tool. Search availability/results can change; discuss returned sources during the lesson.

### M1_07_tool_file_search.py — vector store and file search

**Portal first:** Confirm the model/API supports Responses API file search and vector stores. Ensure the key can create, upload, query, and delete vector-store files. Review the sample policy document before upload; use only approved non-sensitive classroom data.

**Run:** `python demos/m1/M1_07_tool_file_search.py` from the project root.

**Show:** The code creates a remote vector store, uploads and indexes `sample_data/expenses_policy.txt`, queries it with `file_search`, and attempts to delete the vector store in `finally`. Check Foundry for leftovers if execution is interrupted before cleanup; manually delete any orphaned teaching vector store after the demo. Service retention/deletion behavior is governed by Azure settings.

### M1_08_tool_function_call.py — application function calling

**Portal first:** A project and Responses API deployment are enough; no remote tool service is provisioned because `get_demo_time` is local application code.

**Run:** `python demos/m1/M1_08_tool_function_call.py`.

**Show:** The schema describes the function. The model can request it, but Python checks the function name and executes the local function, then sends the result back with the matching `call_id`.

### M1_09_rag_local_context.py — retrieval augmented generation

**Portal first:** Same project and Responses deployment. No portal vector index is needed: the example uses a small local keyword retriever so the three RAG stages are visible.

**Run:** `python demos/m1/M1_09_rag_local_context.py`; ask about the taxi limit or receipt requirement.

**Show:** Retrieved source lines are printed, inserted into the prompt as grounding evidence, then passed to the model. This is a teaching retriever, not a production-quality semantic search system.

### M1_10_model_comparison.py — compare deployed models

**Portal first:** Deploy two or more models you are allowed to use. Ensure they are accessible through the same configured endpoint. Their deployment names must be known. For one deployment, no extra setting is needed.

**Run one deployment:** `python demos/m1/M1_10_model_comparison.py`

**Run two deployments (PowerShell):** `$env:M1_COMPARE_MODELS="deployment-a,deployment-b"; python demos/m1/M1_10_model_comparison.py`

**Show:** The script holds the prompt constant and prints response time, reported tokens, and output. This is a classroom comparison, not a statistically controlled benchmark or an evaluation of cost/safety. Unset after the demo with `Remove-Item Env:M1_COMPARE_MODELS`.

### M1_11_manual_evaluation.py — human evaluation

**Portal first:** Same configured deployment. For richer comparison, deploy another model and repeat after updating `.env`.

**Run:** `python demos/m1/M1_11_manual_evaluation.py`; read each model answer and enter a human score plus note.

**Show:** Compare against expected outcomes and discuss relevance, fluency, correctness, and safety. The human review is intentional; no uncalibrated scoring algorithm is presented as a reliable evaluator.

### M1_12_finetuned_model_evaluation.py — evaluate a fine-tuned deployment

**Portal/workflow first:** This script does **not** create or fine-tune a model. First verify the current Foundry/Azure fine-tuning workflow supports the model family and region you plan to teach. Prepare an approved JSONL training set in the required format with representative prompt/completion examples; remove sensitive or unapproved data. In the portal or supported Azure workflow, upload/validate the training file, create and monitor a fine-tuning job, review its result, then deploy the resulting fine-tuned model. Copy that deployment's endpoint/key/deployment name into `.env` as `AZURE_AI_FOUNDRY_*`. Have a separate held-out test set; do not judge quality on training examples alone. Fine-tuning availability and exact portal screens are model- and service-dependent.

**Run:** `python demos/m1/M1_12_finetuned_model_evaluation.py`.

**Show:** Explain that fine-tuning aims at consistent behavior, style, or output format. Compare the output against held-out examples and a base model. It does not add current facts; use RAG when current or private source data must ground answers.

### M1_13_responsible_ai_review.py — responsible AI checkpoint

**Portal first:** Same project and deployment. The sample creates no content-filter configuration. If demonstrating actual Azure content filters/guardrails, configure and test them separately in the Foundry portal for the chosen deployment.

**Run:** `python demos/m1/M1_13_responsible_ai_review.py`; enter a classroom sample request and discuss the draft before approving/holding it.

**Show:** Map, measure, mitigate, and manage are lifecycle activities. The prompt and human checkpoint illustrate discussion; they are not a substitute for deployed guardrails, monitoring, or an impact assessment.

### M1_14_capstone_expense_assistant.py — combined use case

**Portal first:** Same Responses-compatible project and deployment. No hosted vector store is used; the policy is local and synthetic. Use only the included teaching policy. If trying a hosted deployment, ensure tool/function calling is supported.

**Run:** `python demos/m1/M1_14_capstone_expense_assistant.py`; try a question such as “What is the taxi limit?” and a separate explicit request such as “Draft a claim for a $42 taxi ride for airport travel.”

**Show:** The local retriever fetches policy lines, prompt instructions treat them as data, and the model may request a validated local draft function. It never submits or pays a claim. A human must verify the answer and draft.

### M1_15_endpoint_configuration.py — endpoint setup comparison

**Portal first:** For the Foundry line, configure `AZURE_AI_FOUNDRY_*`. To show the Azure OpenAI line as well, separately obtain the Azure OpenAI `/openai/v1` endpoint, key, and deployment, and set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_MODEL` in `.env`.

**Run:** `python demos/m1/M1_15_endpoint_configuration.py`.

**Show:** Both lines construct OpenAI SDK clients, while `base_url` selects the service endpoint and the deployment name selects the model. Construction does not send a model request.

## Troubleshooting

- **Missing setting:** Confirm `.env` is in the repository root, not inside `demos`, and values have no surrounding quotes or placeholder text.
- **401/403:** Check key, endpoint pairing, deployment access, subscription/project permissions, and network policy.
- **Deployment not found:** Use the exact deployment name, not just the model family name.
- **Unsupported tool / bad request:** Verify model, API version, region and tool support in Foundry; not every model supports every Responses API tool.
- **No module named openai/dotenv:** Activate the project `.venv` and reinstall requirements in that environment.
- **File search left an asset behind:** Look for the `m1-expenses-policy-demo` vector store in the service and delete it if no longer needed.

## Sample inputs and expected outputs

Before presenting, see [M1_DEMO_SAMPLE_INPUTS_AND_OUTPUTS.md](M1_DEMO_SAMPLE_INPUTS_AND_OUTPUTS.md) for copy-ready prompts, multi-turn examples, and illustrative outputs for all 15 demos. Generated text and live service results vary, so treat those responses as examples rather than guaranteed exact strings. The end of each `demos/m1/M1_*.py` file also has its own quick sample block.





