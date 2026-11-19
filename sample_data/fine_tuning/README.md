# M1 fine-tuning practice data

- `training.jsonl` has 18 synthetic travel-support classification examples.
- `validation.jsonl` has 6 separate examples. The evaluation script reads these and reports exact-label agreement.

Each line is a JSON object containing a `messages` array: a system task instruction, a user message, and the target assistant label. This is chat-style JSONL for supervised fine-tuning.

The small set is for teaching the shape of the data, not a claim that every model will accept it. Before uploading, check the selected model's current minimum number of examples, maximum file size, format, region, and fine-tuning eligibility in Microsoft Foundry. If it requires more examples, add distinct, balanced, reviewed data; do not duplicate these rows just to meet a minimum. Do not include real student/customer data or secrets.

