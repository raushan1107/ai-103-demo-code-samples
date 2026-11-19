"""M1 demo: Human review checkpoint.

Run from the project root: python demos/m1/M1_13_responsible_ai_review.py
Generates a draft and asks the user whether to approve or hold it.
Related slides: 8, 46-49. A prompt is not a complete safety control.
"""
from common import foundry_client


def main() -> None:
    client, model = foundry_client()
    user_text = input("Enter a sample user request: ").strip()
    # Ask for uncertainty and limits so they are visible for the review discussion.
    response = client.responses.create(
        model=model,
        instructions=(
            "Be careful and transparent. Avoid requesting personal sensitive data. "
            "For harmful or expert-dependent requests, state a limitation and safe next step."
        ),
        input=user_text,
    )
    print(f"\nDraft response:\n{response.output_text}")
    print("Review: fairness, reliability/safety, privacy/security, inclusion, transparency, accountability")
    decision = input("Approve this classroom response? (yes/no): ").strip().lower()
    if decision == "yes":
        print("Approved for discussion.")
    else:
        print("Hold it, identify the issue, revise controls, then review again.")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_13.
# Before running: configure .env. For actual guardrails, configure them separately in Foundry.
# Command from the project root: python demos/m1/M1_13_responsible_ai_review.py

# Sample input and expected output for classroom demonstration:
# Sample input: Explain how to create a strong password. Sample approval input: yes (or no to hold it).
# Example behavior: draft guidance then approval/hold message. This is a review exercise, not an automated guardrail.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_13_responsible_ai_review.py
# Enter a request, inspect the draft, then choose whether to approve or hold it.
