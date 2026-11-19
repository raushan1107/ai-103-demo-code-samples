"""M1 demo: Compare model deployments.

Run from the project root: set M1_COMPARE_MODELS=model-a,model-b; python demos/m1/M1_10_model_comparison.py
Sends one shared prompt to one or more deployments and compares outputs.
Related slides: 12-15. This small manual comparison is not a formal benchmark.
"""
import os
import time
from common import foundry_client


def main() -> None:
    client, default_model = foundry_client()
    # Optional list of comma-separated deployment names enables side-by-side review.
    models = [name.strip() for name in os.getenv("M1_COMPARE_MODELS", default_model).split(",")]
    prompt = "Explain retrieval augmented generation to a new developer in three bullets."
    for model in models:
        started = time.perf_counter()
        # Keep prompt and sampling settings constant while changing only the deployment.
        response = client.responses.create(model=model, input=prompt, temperature=0)
        elapsed = time.perf_counter() - started
        usage = response.usage
        token_count = usage.total_tokens if usage else "not reported"
        print(f"\n=== {model}: {elapsed:.2f}s, {token_count} total tokens ===")
        print(response.output_text)
    print("Discuss quality and safety separately; timing varies with service load and network.")


if __name__ == "__main__":
    main()


# Run guide: see guides/M1_DEMOS_RUN_GUIDE.md, section M1_10.
# Before running: deploy models to compare; set M1_COMPARE_MODELS to comma-separated names.
# Command (PowerShell): $env:M1_COMPARE_MODELS="model-a,model-b"; python demos/m1/M1_10_model_comparison.py

# Sample input and expected output for classroom demonstration:
# Sample PowerShell setup: $env:M1_COMPARE_MODELS="deployment-a,deployment-b"
# Example output: one generated answer block per deployment with elapsed seconds and token count; values vary.

# M1 demo workflow/run reminder:
# Run from the project root in the VS Code terminal: python demos/m1/M1_10_model_comparison.py
# This script sends the example prompt shown in main() to the configured deployment.
