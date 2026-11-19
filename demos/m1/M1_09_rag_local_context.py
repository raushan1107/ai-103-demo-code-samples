"""M1 demo: Local retrieval augmented generation.

Run from the project root: python demos/m1/M1_09_rag_local_context.py
Retrieves matching local policy lines and provides them as grounded context.
"""

from common import ROOT, foundry_client


def retrieve_passages(question: str, document: str) -> list[str]:
    """Select lines sharing query terms, standing in for a retrieval component."""
    terms = {word.strip(".,?!:").lower() for word in question.split() if len(word) > 3}
    ranked = []
    for line in document.splitlines():
        score = sum(term in line.lower() for term in terms)
        if score:
            ranked.append((score, line.strip()))
    # Highest-overlap lines are the grounding context passed to generation.
    return [line for _, line in sorted(ranked, reverse=True)[:3]]


def main() -> None:
    client, model = foundry_client()
    document_path = ROOT / "sample_data" / "expenses_policy.txt"
    document = document_path.read_text(encoding="utf-8")
    question = input("Ask about the expense policy: ").strip()

    # RETRIEVE: find relevant local lines based on the question.
    passages = retrieve_passages(question, document)
    if not passages:
        print("No matching policy passages were retrieved; try different wording.")
        return

    # AUGMENT: put retrieved source text into a clearly delimited section.
    context = "\n".join(f"- {passage}" for passage in passages)
    prompt = f"Policy passages:\n{context}\n\nQuestion: {question}"

    # GENERATE: constrain the model to the evidence so answers remain grounded.
    response = client.responses.create(
        model=model,
        instructions=(
            "Answer using only the policy passages. If they do not support an answer, "
            "say the policy does not specify."
        ),
        input=prompt,
    )
    print(f"\nRetrieved evidence:\n{context}\n\nAnswer: {response.output_text}")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_09.
# Before running: configure .env; this lesson uses the included local policy file.
# Command from the project root: python demos/m1/M1_09_rag_local_context.py; ask about the expense policy.

# Sample input and expected output for classroom demonstration:
# Sample inputs: What is the taxi limit? | What should I include with an expense claim?
# Example outputs: USD 75 per trip | include the business purpose and receipt. Retrieved evidence prints before the answer.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_09_rag_local_context.py
# Enter a policy question. Local matching retrieves evidence before the model call.
