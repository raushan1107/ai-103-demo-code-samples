"""M1 demo: Prompt engineering.

Run from the project root: python demos/m1/M1_04_prompt_engineering.py
Shows instructions, examples, and an output format in one request.
Related slides: 40-41. This illustrates prompt design; it does not retrain a model.
"""

from common import foundry_client


def main() -> None:
    client, model = foundry_client()

    # The system instruction sets role, scope, tone, and a rule for uncertainty.
    system_instructions = (
        "You are a clear Python tutor. Answer only Python programming questions. "
        "Use a friendly tone. If important context is missing, ask one question. "
        "Format answers with a short explanation and a tiny code example."
    )

    # Few-shot examples demonstrate the desired input/output pattern explicitly.
    examples = """Example:
Question: What is a list?
Answer: A list stores an ordered collection. Example: colors = [\"red\", \"blue\"]

Example:
Question: What is a dictionary?
Answer: A dictionary maps keys to values. Example: user = {\"name\": \"Ava\"}
"""

    # A template makes the desired output structure visible and repeatable.
    question = input("Ask a Python question: ").strip()
    prompt = (
        f"{examples}\nNow answer the next question using the same style.\n"
        f"Question: {question}\n"
        "Answer using: Definition, Example, One thing to remember."
    )

    # Temperature controls sampling variability where the selected model supports it.
    response = client.responses.create(
        model=model,
        instructions=system_instructions,
        input=prompt,
        #temperature=0.5,

        # higher temperature (e.g., 0.7) can produce more creative answers, but may be less consistent.
        # for example: in response to "What is a list?", a higher temperature might produce an answer that includes 
        # a joke or an unrelated fact, while a lower temperature will produce a more straightforward answer.
    )
    print(f"\n{response.output_text}")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_04.
# Before running: configure .env for a Responses-compatible Foundry deployment.
# Command from the project root: python demos/m1/M1_04_prompt_engineering.py; enter a question when prompted.

# Sample input and expected output for classroom demonstration:
# Sample input: Explain a Python list. Optional second run: What is the capital of France?
# Example expected output: a definition, tiny Python example, and reminder; for unrelated input, a polite redirect to Python.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_04_prompt_engineering.py
# Enter a Python question. Read the instruction, examples, and requested output template above.
