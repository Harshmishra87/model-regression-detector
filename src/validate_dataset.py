import json
import sys
from collections import Counter

REQUIRED_FIELDS = {"id", "input", "expected_category", "expected_summary"}
ALLOWED_CATEGORIES = {"billing", "technical", "account", "general"}


def validate_dataset(path: str) -> bool:
    with open(path) as f:
        cases = json.load(f)

    ids_seen = set()
    errors = []

    for case in cases:
        missing = REQUIRED_FIELDS - case.keys()
        if missing:
            errors.append(f"{case.get('id', '?')}: missing fields {missing}")

        if case["id"] in ids_seen:
            errors.append(f"Duplicate id: {case['id']}")
        ids_seen.add(case["id"])

        if case.get("expected_category") not in ALLOWED_CATEGORIES:
            errors.append(f"{case['id']}: invalid category '{case.get('expected_category')}'")

        if not case.get("input", "").strip():
            errors.append(f"{case['id']}: empty input")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        return False

    print(f"Validation passed: {len(cases)} cases OK.")
    return True


def check_balance(cases: list[dict], min_per_category: int = 10) -> None:
    category_counts = Counter(c["expected_category"] for c in cases)
    difficulty_counts = Counter(c.get("expected_difficulty", "unspecified") for c in cases)

    print("Category distribution:", dict(category_counts))
    print("Difficulty distribution:", dict(difficulty_counts))

    for category, count in category_counts.items():
        if count < min_per_category:
            print(f"WARNING: '{category}' has only {count} cases (min recommended: {min_per_category})")

    for expected in ["billing", "technical", "account", "general"]:
        if category_counts.get(expected, 0) == 0:
            raise ValueError(f"Category '{expected}' has zero test cases — cannot evaluate it at all.")


if __name__ == "__main__":
    ok = validate_dataset("data/golden_dataset.json")
    if ok:
        with open("data/golden_dataset.json") as f:
            cases = json.load(f)
        check_balance(cases)
    sys.exit(0 if ok else 1)