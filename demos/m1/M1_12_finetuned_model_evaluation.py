"""M1 demo: Evaluate a deployed fine-tuned model.

Run from the project root: python demos/m1/M1_12_finetuned_model_evaluation.py
Runs held-out examples against a deployment; it does not train a model.
"""
import json
from common import ROOT, foundry_client


def main() -> None:
    client, model = foundry_client()
    validation_path = ROOT / "sample_data" / "fine_tuning" / "validation.jsonl"
    correct = 0
    total = 0

    # Read held-out cases. They were kept separate from training to test generalization.
    with validation_path.open("r", encoding="utf-8-sig") as validation_file:
        for line_number, line in enumerate(validation_file, start=1):
            if not line.strip():
                continue
            example = json.loads(line)
            messages = example["messages"]
            system_text = next(m["content"] for m in messages if m["role"] == "system")
            user_text = next(m["content"] for m in messages if m["role"] == "user")
            expected = next(m["content"] for m in messages if m["role"] == "assistant")

            # Ask for a single classification using the same task instruction as training.
            response = client.responses.create(
                model=model,
                instructions=system_text,
                input=user_text,
                temperature=0,
            )
            predicted = response.output_text.strip()
            is_correct = predicted.casefold() == expected.casefold()
            correct += int(is_correct)
            total += 1
            print(
                f"{line_number:02d}. {user_text}\n"
                f"    expected: {expected} | predicted: {predicted} | "
                f"{'PASS' if is_correct else 'REVIEW'}"
            )

    # This tiny dataset is a classroom check, not a statistically reliable benchmark.
    accuracy = correct / total if total else 0.0
    print(f"\nDeployment: {model}")
    print(f"Held-out exact-label accuracy: {correct}/{total} ({accuracy:.0%})")
    print("Review every mismatch; also compare these same cases with the base deployment.")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_12_FINETUNING_STUDENT_LAB.md for the portal walkthrough.
# Portal first: prepare/validate data, submit and monitor an SFT job, then deploy it.
# Put the deployed fine-tuned model's exact deployment name in AZURE_AI_FOUNDRY_MODEL.
# Command from the project root: python demos/m1/M1_12_finetuned_model_evaluation.py

# Sample input and expected output for classroom demonstration:
# Sample extra playground inputs: Could you move my return flight to Sunday? -> Booking change,
# Does this fare include a checked bag? -> Travel information, Please refund the cancelled tour -> Refund.
# This script reads validation.jsonl and prints expected/predicted/PASS or REVIEW and exact-label accuracy.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_12_finetuned_model_evaluation.py
# Uses sample_data/fine_tuning/validation.jsonl; it evaluates an existing deployment only.
