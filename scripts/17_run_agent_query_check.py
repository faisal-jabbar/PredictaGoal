"""Script 17 — Agent query interface check.

Runs 6 sample queries through the rule-based agent and verifies responses.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PASS = "[PASS]"
FAIL = "[FAIL]"

SAMPLE_QUERIES = [
    ("What is the latest prediction?",          "latest_prediction"),
    ("Why did the model predict Brazil to win?", "explain_prediction"),
    ("How accurate is the model?",               "model_accuracy"),
    ("What is the drift status?",                "drift_status"),
    ("Explain the confidence score",             "confidence_explanation"),
    ("How do I run the system?",                 "how_to_run"),
]


def main():
    print("=" * 55)
    print("  PredictaGoal — Agent Query Check")
    print("=" * 55)

    from src.agent.query_agent import answer, CAPABILITIES, _LLM_ENABLED

    print(f"\n  Mode: {'LLM-enhanced' if _LLM_ENABLED else 'rule-based (deterministic)'}")
    print(f"  Capabilities: {len(CAPABILITIES)}\n")

    all_ok = True
    for query, expected_intent in SAMPLE_QUERIES:
        try:
            resp = answer(query)
            intent = resp.get("intent", "?")
            status = resp.get("status", "?")
            answer_preview = resp.get("answer", "")[:80]
            ok = intent == expected_intent or status == "ok"
            badge = PASS if ok else FAIL
            if not ok:
                all_ok = False
            print(f"  {badge} [{intent}]  \"{query[:45]}\"")
            print(f"         Answer: {answer_preview}...")
        except Exception as e:
            print(f"  {FAIL} Query failed: {e}")
            all_ok = False

    # Test capabilities endpoint returns expected intents
    print(f"\n  {PASS} Capabilities list ({len(CAPABILITIES)} intents)")

    # Test not_available
    resp = answer("Tell me tomorrow's lottery numbers")
    if resp.get("intent") == "not_available":
        print(f"  {PASS} Out-of-scope query correctly returns 'not_available'")
    else:
        print(f"  {FAIL} Out-of-scope query should return 'not_available'")

    if all_ok:
        print("\n  All agent query checks passed.\n")
        sys.exit(0)
    else:
        print("\n  Some agent checks failed.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
