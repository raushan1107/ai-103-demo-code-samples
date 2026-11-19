# Module 2 demo prompts and expected behavior

Generated text may vary. The point of each demo is the visible execution pattern, not an exact model response.

| Demo | Input | Expected behavior |
| --- | --- | --- |
| M2_01 First agent | Fixed prompt about Python lists | Agent answers briefly with a small list example. |
| M2_02 Custom function | Fixed Seattle weather question | Agent calls the typed Python function and labels its fixed fictional result as sample data. |
| M2_03 Foundry function call | `Add 18 and 24` | Foundry agent requests `add_numbers`; local Python returns `42`; a follow-up Responses call explains the result. |
| M2_04 + M2_05 MCP | Ask what MCP means in the course | Agent discovers and calls the local `lookup_course_topic` server tool and summarizes its text. |
| M2_06 Foundry IQ | A question in the provisioned knowledge source | Agent invokes `knowledge_base_retrieve` through the configured project connection and answers with retrieved information/citations when present. |
| M2_07 Sequential agents | `Checkout failed for about five minutes after a database restart. Service recovered.` | Drafter summarizes; reviewer sees prior context and returns a checked summary. |
| M2_08 Existing Foundry agent | First turn and a follow-up | Both turns use the configured portal agent and same conversation; the response can use that agent's server-side tools/instructions. |

The Foundry IQ row requires real provisioned knowledge-base data; the script does not supply or fabricate an expected policy answer.
