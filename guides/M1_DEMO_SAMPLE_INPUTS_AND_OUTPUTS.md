# Teaching examples: sample inputs and expected outputs

The end-of-file comments in each `demos/m1/M1_*.py` file contain copy-ready sample inputs and expected output examples. This guide gathers them in one place for lesson preparation. Generated wording, model classifications, latency, token counts, tool availability, and live search results can vary; outputs below are illustrative unless the demo is a deterministic local function or fixed data lookup.

| Demo | Sample input | Example expected output / behavior |
| --- | --- | --- |
| M1_01 First response | Fixed prompt: `What is the capital of France?` | `Answer: Paris.` Wording may vary. |
| M1_02 Responses conversation | `What is photosynthesis?` then `Explain it in one sentence for a 10-year-old.` then `quit` | First answer defines photosynthesis; second uses prior context. Prints goodbye after `quit`. |
| M1_03 Chat Completions | `When was Microsoft founded?` then `Who founded it?` then `quit` | First answers April 4, 1975; second refers to Bill Gates and Paul Allen. Exact wording may vary. |
| M1_04 Prompt engineering | `Explain a Python list.`; optionally `What is the capital of France?` | A structured definition/example/remember item; unrelated request should be declined or redirected to Python. |
| M1_05 Code Interpreter | Fixed area question: `A room is 8.5 meters by 6 meters. What is its area in square feet?` | Approximately `548.96 square feet` (51 square meters converted). Natural language may vary. |
| M1_06 Web search | Fixed question about two recent Microsoft AI announcements | A short summary with current source links, if search is available. Verify links live; results change. |
| M1_07 File search | Fixed question: `What is the maximum reimbursable taxi fare?` | Based on included policy: `USD 75 per trip`; cite/refer to policy evidence if returned. |
| M1_08 Function calling | Fixed request: `What time is it in the demo time zone?` | Local Asia/Kolkata time in `YYYY-MM-DD HH:MM:SS IST` style; the actual time changes. |
| M1_09 Local RAG | `What is the taxi limit?` or `What should I include with a claim?` | Shows retrieved policy text then a grounded answer: USD 75 per trip, or business purpose and receipt. |
| M1_10 Model comparison | Set `M1_COMPARE_MODELS="deployment-a,deployment-b"` in PowerShell | One output block per model with generated bullets, elapsed seconds and token count; values vary. |
| M1_11 Manual evaluation | On prompts: `What is the taxi reimbursement limit?` and `What should accompany an expense claim?`; enter scores such as `5 - correct and clear` | Prints model answer beside expected answer, then records the student's score/note. Model answer may vary. |
| M1_12 Fine-tuned model | No interactive input; reads the six examples from `sample_data/fine_tuning/validation.jsonl` | Prints expected vs predicted label and PASS/REVIEW for each, then exact-label accuracy. Scores depend on training and deployment. |
| M1_13 Responsible AI | Example safe request: `Explain how to create a strong password.`; discuss draft, answer `yes` or `no` at approval prompt | Model draft followed by approval or hold message. This illustrates review, not a complete guardrail. |
| M1_14 Capstone | `What is the taxi limit?` or `Draft a claim for a $42 taxi ride for airport travel.` | First should answer from policy. Second may draft USD 42 but must say it is only a draft; no claim is submitted. |
| M1_15 Endpoint configuration | No prompt entered | Reports which endpoint/client configurations are ready; makes no model call. |

## Useful class input set

For the policy demos, these comma-separated prompts exercise distinct paths: `What is the taxi reimbursement limit?`, `What should I include with an expense claim?`, `Is a $90 taxi fare automatically reimbursed?`, `Draft a claim for a $42 taxi ride for airport travel.` Use one at a time when the script prompts for a single input. The policy only says fares above $75 require manager approval before travel; it does not guarantee reimbursement.

For the travel-classifier fine-tuned model, try held-out messages such as: `Could you move my return flight to Sunday?` → `Booking change`, `Does this fare include a checked bag?` → `Travel information`, `Please return the payment for the cancelled tour.` → `Refund`. The script itself evaluates the six validation rows; these extra prompts are useful in the Foundry playground.

