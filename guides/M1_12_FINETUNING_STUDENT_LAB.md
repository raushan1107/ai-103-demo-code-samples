# Student lab: fine-tune a travel message classifier in Microsoft Foundry

This is a screen-share friendly walkthrough for **M1_12_finetuned_model_evaluation.py**. It uses synthetic travel-support examples and teaches supervised fine-tuning (SFT) for consistent classification labels. Fine-tuning is an optional practice activity: check current model, region, quota, permissions, and pricing before starting. Portal labels and available models can change.

## Files for the lab

- `sample_data/fine_tuning/training.jsonl` — 18 labeled training conversations.
- `sample_data/fine_tuning/validation.jsonl` — 6 different labeled examples for validation during training.
- `sample_data/fine_tuning/README.md` — data format and checks.
- `demos/m1/M1_12_finetuned_model_evaluation.py` — calls an already deployed tuned model on held-out examples.

Each JSONL line is one complete training example. The `system` message gives the task and the allowed labels; `user` supplies a message; `assistant` is the desired target answer. Keep one JSON object per physical line. Do not add comments or a comma between lines. The final line may end with a newline.

## Before class: check access and cost

1. Sign in to [Microsoft Foundry](https://ai.azure.com/) and select the project/resource you intend to use.
2. Open **Build > Fine-tune** (some portal versions may show **Fine-tuning**). Check that at least one listed model supports **Supervised fine-tuning** in your project’s region.
3. Open the model's fine-tuning details/requirements. Confirm the required training and validation formats, minimum example count, maximum file size, eligible region, and any special permissions. These limits vary by model and may be larger than the small teaching sample in this folder.
4. Confirm your role permits training. You may need a Foundry User (or equivalent training permission). Deploying the result requires Foundry Owner or deployment-write permission. Ask the subscription/project administrator if the portal blocks either action.
5. Review current training and deployment pricing, available quota, and any minimum hosting duration before starting. Fine-tune jobs and a running model deployment can incur charges. Do not use personal, confidential, or regulated data in this classroom exercise.
6. If the sample count is below the selected model's minimum, do not submit it unchanged. Either select a model whose current requirements it meets or prepare more reviewed, balanced examples using the same format. Never duplicate examples just to satisfy a minimum.

Official references: [SFT data and portal job steps](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning), [fine-tuning overview and supported models](https://learn.microsoft.com/en-us/azure/foundry/concepts/fine-tuning), [deploying a fine-tuned model](https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/deploy-fine-tuned-models).

## Part A — inspect and prepare the data

1. In VS Code, open `sample_data/fine_tuning/training.jsonl` and `validation.jsonl`.
2. Explain that JSONL means JSON Lines: one JSON object per line. These are chat-format examples with `messages` containing role/content pairs.
3. Point to the system instruction and show that every assistant target is exactly one of three permitted labels: `Booking change`, `Travel information`, or `Refund`.
4. Keep validation examples separate. They are used to check generalization during training; do not copy them into training.
5. Before uploading, confirm the selected model accepts this chat format and that both files meet its current counts, size, and other constraints. Portal validation is authoritative.
6. If the model requires more examples, create additional *distinct and reviewed* examples for each class. Keep the classes reasonably balanced and reserve new examples for validation and final testing.

The included sample is intentionally small for teaching and may **not** meet the minimum requirements of every currently supported model. It is not a guarantee that a job will be accepted.

## Part B — create the SFT job in the portal

Portal UI can change; use the fine-tuning page for your project and follow the labels currently shown.

1. In Foundry, open the correct project.
2. Select **Build > Fine-tune** or **Fine-tuning**, then select **Fine-tune** / **Create fine-tuning job**.
3. Select a currently supported **base model**. Open its details and confirm SFT eligibility, region, format, training limits, and deployment options. Do not assume every catalog model can be fine-tuned.
4. Choose **Supervised fine-tuning (SFT)** as the customization method.
5. Choose the training type and any required compute option shown for that model/resource.
6. For training data, choose **Upload new dataset** (or equivalent), then upload `training.jsonl` from `sample_data/fine_tuning/`.
7. For validation data, upload `validation.jsonl` separately. If optional, use it for this practice so learners can see validation metrics. Make sure no validation examples also appear in training.
8. Inspect the preview and validation messages. Fix every format or content error before continuing. The portal may tell you if there are too few examples or if the selected model expects a different format.
9. Give the job a recognizable name/suffix such as `m1-travel-classifier-demo` if offered.
10. For a first practice run, keep the model's recommended/default hyperparameters unless the portal requires a selection. Avoid changing several settings at once.
11. Review the selected model, uploaded files, region, estimated or displayed cost, and any terms. Start/submit only after reviewing these with the class.

## Part C — monitor and inspect the job

1. Open the fine-tuning jobs list in the same project.
2. Select the job and show its status, events, and available metrics/logs. Status names can vary; wait until the portal reports completion/success before expecting a deployable result.
3. If it fails, open the job details/events and read the reason. Common causes include unsupported model/region combinations, invalid JSONL, too few examples, file limits, quota, or permissions. Correct the cause and submit a new job only after checking for any cost implications.
4. Review training and validation metrics. Training examples alone do not demonstrate generalization; use validation and additional held-out examples.
5. Keep a note of the completed fine-tuned model identifier and job record needed by the deployment flow. Do not assume that a completed training job is already a callable endpoint.

## Part D — deploy and test the tuned model

1. Open the completed job details and select **Deploy** (or the currently offered deployment action).
2. Choose one of the deployment options supported by this fine-tuned model and project. If no option is available, check model support, deployment quota, region, and permissions.
3. Enter a unique deployment name, for example `m1-travel-classifier-ft`. The deployment name is what the inference script uses as the `model` value.
4. Review capacity/SKU and displayed price before creating the deployment. Start the deployment and monitor it in the portal until its status is ready/succeeded.
5. In the Foundry playground, select the **fine-tuned deployment**, not the base model. Ask a message not present in either JSONL file, such as “Could you move my return flight to Sunday?” Expected label: `Booking change`.
6. Try one fresh example from each class, then compare results with the base model using the same inputs. Discuss whether format and behavior are more consistent. Fine-tuning does not add current travel facts or replace retrieval for changing information.

## Part E — run the Python evaluation demo

1. Copy the deployed fine-tuned deployment name from Foundry.
2. In the project-root `.env`, set `AZURE_AI_FOUNDRY_MODEL` to that exact deployment name. Keep the endpoint and key paired with the Foundry resource that hosts it.
3. From the project root in the VS Code terminal, run:

   `python demos/m1/M1_12_finetuned_model_evaluation.py`

4. Compare its classifications with the base deployment and validation/held-out examples. Record misses and discuss the next data improvements; do not evaluate only on training examples.

The API and model must support the endpoint/API used by this script. If you receive a model/API compatibility error, test in the Foundry playground and verify the deployment's supported inference API before changing the code.

## Part F — clean up after practice

1. Delete the serving deployment when the class no longer needs it; an active deployment may continue to incur hosting charges.
2. Delete training/validation files and the fine-tuned model only if no longer needed and you have retained any records required for the exercise. Follow your organization's retention requirements.
3. Keep the job record only as long as needed for the class. Check the portal's current deletion and retention behavior.

## Screen-share and student screenshot checklist

Take screenshots of these **non-secret** screens, if your organization allows sharing them:

1. Fine-tuning page showing the model/method selector and current support information.
2. VS Code showing one JSONL example (hide unrelated files and personal details).
3. Dataset upload preview with filenames and a successful validation result (do not include sensitive data).
4. Job configuration summary before submission (hide subscription IDs and any identifiers your organization treats as confidential).
5. Job status/metrics after completion.
6. Deployment ready status and playground using a held-out input.
7. Python terminal output from `demos/m1/M1_12_finetuned_model_evaluation.py`.

Never share API keys, `.env`, access tokens, personal data, or confidential training examples in screenshots. The portal is the source of truth for model availability, file rules, permission requirements, and current costs.


