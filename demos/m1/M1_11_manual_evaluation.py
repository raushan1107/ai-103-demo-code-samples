"""M1 demo: Human evaluation.

Run from the project root: python demos/m1/M1_11_manual_evaluation.py
Compares generated answers with expected points and records human feedback.
Related slides: 15-17. This teaches review dimensions without pretending to automate them.
"""
from common import foundry_client

CASES = [
    ("What is the taxi reimbursement limit?", "USD 75 per trip in our teaching policy."),
    ("What should accompany an expense claim?", "The business purpose and receipt."),
]


def main() -> None:
    client, model = foundry_client()
    for question, expected in CASES:
        # Use the same instruction pattern per case to make outputs easier to compare.
        response = client.responses.create(
            model=model,
            instructions="Answer in one sentence; say when you do not know.",
            input=question,
        )
        print(f"\nQuestion: {question}\nModel: {response.output_text}\nExpected: {expected}")
        # The learner records a human judgement, not a metric fabricated by the script.
        print("Review relevance, fluency, correctness, and safety.")
        print(f"Human score (1-5) and note: {input().strip()}")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_11.
# Before running: configure at least one deployed model in .env.
# Command from the project root: python demos/m1/M1_11_manual_evaluation.py; enter a human score and note per case.

# Sample input and expected output for classroom demonstration:
# Sample prompts: What is the taxi reimbursement limit? | What should accompany an expense claim?
# Sample score entry per case: 5 - correct and clear. Output compares model text with expected text; model wording can vary.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_11_manual_evaluation.py
# For each fixed evaluation question, enter your own score and short review note.
