def index_by_id(scored_results: list[dict]) -> dict:
    return {r["id"]: r for r in scored_results}


def diff_runs(current: list[dict], previous: list[dict]) -> dict:
    cur_by_id = index_by_id(current)
    prev_by_id = index_by_id(previous)

    regressions, improvements, unchanged = [], [], []

    for case_id, cur in cur_by_id.items():
        prev = prev_by_id.get(case_id)
        if prev is None:
            continue  # new case, nothing to diff against yet

        cur_pass = cur["category_score"] == 1 and cur["quality_score"] >= 3
        prev_pass = prev["category_score"] == 1 and prev["quality_score"] >= 3

        if prev_pass and not cur_pass:
            regressions.append(case_id)
        elif not prev_pass and cur_pass:
            improvements.append(case_id)
        else:
            unchanged.append(case_id)

    cur_pass_rate = sum(c["category_score"] for c in current) / len(current)
    prev_pass_rate = sum(c["category_score"] for c in previous) / len(previous)

    return {
        "regressions": regressions,
        "improvements": improvements,
        "unchanged_count": len(unchanged),
        "pass_rate_delta": cur_pass_rate - prev_pass_rate,
        "current_pass_rate": cur_pass_rate,
        "previous_pass_rate": prev_pass_rate,
    }