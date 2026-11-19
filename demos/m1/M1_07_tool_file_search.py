"""M1 demo: Hosted file search.

Run from the project root: python demos/m1/M1_07_tool_file_search.py
Uploads the teaching policy, queries a vector store, and attempts cleanup.
Related slides: 28, 31, 35. This creates remote vector-store assets and may incur cost.
"""

from common import ROOT, foundry_client


def main() -> None:
    client, model = foundry_client()
    policy_path = ROOT / "sample_data" / "expenses_policy.txt"
    if not policy_path.exists():
        raise FileNotFoundError(f"Add the teaching sample document at {policy_path}")

    # Create a managed vector store; uploaded files are indexed for semantic retrieval.
    vector_store = client.vector_stores.create(name="m1-expenses-policy-demo")
    try:
        # Open as binary because the SDK uploads the original file bytes.
        with policy_path.open("rb") as policy_file:
            client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=policy_file,
            )

        # file_search attaches retrieved document passages to the model's context.
        response = client.responses.create(
            model=model,
            instructions=(
                "Answer only from the supplied expenses policy. If it does not say, "
                "clearly say the policy does not specify."
            ),
            input="What is the no of days of leave allowed?",
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store.id],
                }
            ],
            include=["file_search_call.results"],
        )
        print(response.output_text)
    finally:
        # Clean up demo cloud resources to avoid leaving uploaded material behind.
        client.vector_stores.delete(vector_store.id)


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_07.
# Before running: verify vector-store/file-search permissions and review the sample file.
# Command from the project root: python demos/m1/M1_07_tool_file_search.py; check for remote leftovers if interrupted.

# Sample input and expected output for classroom demonstration:
# Showcase input (already in the code): What is the maximum reimbursable taxi fare?
# Example expected output from sample_data/expenses_policy.txt: USD 75 per trip, with policy-grounded explanation.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_07_tool_file_search.py
# The script uploads the included teaching policy, queries it, then attempts vector-store cleanup.
