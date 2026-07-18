import asyncio
import json
import sys

from src.llm_feature import load_prompt_config
from src.runner import run_evaluation
from src.persistence import save_run
from src.scoring import score_case
from src.compare import diff_runs
from src.thresholds import classify_severity, update_history_and_check_drift
from src.report import generate_report
from src.alert import send_slack_alert

MODEL = "gemini-3.1-flash-lite"
REQUESTS_PER_MINUTE = 15


async def score_all(dataset: list[dict], run_results: list[dict], delay: float) -> list[dict]:
    dataset_by_id = {c["id"]: c for c in dataset}
    scored = []
    for i, result in enumerate(run_results):
        case = dataset_by_id[result["id"]]
        score = await score_case(case, result)
        scored.append(score)
        print(f"Scored {i + 1}/{len(run_results)}")
        if i + 1 < len(run_results):
            await asyncio.sleep(delay)
    return scored


async def main():
    delay = 60.0 / REQUESTS_PER_MINUTE + 1.0

    # 1. Capture the PREVIOUS run's data before anything gets overwritten
    try:
        with open("results/latest.json") as f:
            previous_raw = json.load(f)
    except FileNotFoundError:
        previous_raw = None

    try:
        with open("results/scored_latest.json") as f:
            previous_scored = json.load(f)
    except FileNotFoundError:
        previous_scored = None

    # 2. Load config and dataset
    config = load_prompt_config("prompts/email_classifier_v1.yaml")
    with open("data/golden_dataset.json") as f:
        dataset = json.load(f)

    # 3. Run classification against all cases
    print("Running evaluation...")
    current_raw = await run_evaluation(dataset, config, model=MODEL, requests_per_minute=REQUESTS_PER_MINUTE)
    errors = sum(1 for r in current_raw if r["error"])
    print(f"Ran {len(current_raw)} cases, {errors} errors")

    # 4. Persist this run permanently + as "latest"
    run_path = save_run(current_raw, config, model=MODEL, dataset_path="data/golden_dataset.json")
    print(f"Saved run to: {run_path}")

    # 5. Score the current run
    print("Scoring evaluation...")
    current_scored = await score_all(dataset, current_raw, delay)
    with open("results/scored_latest.json", "w") as f:
        json.dump(current_scored, f, indent=2)

    # 6. If there's no previous run, this is a baseline — nothing to diff against yet
    if previous_scored is None:
        print("No previous run found — this is the baseline. Nothing to compare yet.")
        current_pass_rate = sum(c["category_score"] for c in current_scored) / len(current_scored)
        update_history_and_check_drift(current_pass_rate)
        sys.exit(0)

    # 7. Diff current vs previous
    diff = diff_runs(current=current_scored, previous=previous_scored)
    severity = classify_severity(diff["pass_rate_delta"])
    print(f"Eval result: {severity} (pass rate delta: {diff['pass_rate_delta']:.1%})")

    drift_check = update_history_and_check_drift(diff["current_pass_rate"])
    if drift_check["slow_drift_warning"]:
        print(f"SLOW DRIFT WARNING: 7-run moving average is {drift_check['moving_avg']:.1%}")

    # 8. Build the regressed_cases detail list for the report
    dataset_by_id = {c["id"]: c for c in dataset}
    previous_raw_by_id = {r["id"]: r for r in previous_raw["results"]} if previous_raw else {}
    current_raw_by_id = {r["id"]: r for r in current_raw}

    regressed_cases = []
    for case_id in diff["regressions"]:
        regressed_cases.append({
            "id": case_id,
            "input": dataset_by_id[case_id]["input"],
            "previous_output": previous_raw_by_id.get(case_id, {}).get("output"),
            "current_output": current_raw_by_id.get(case_id, {}).get("output"),
        })

    with open("results/history.json") as f:
        history = json.load(f)

    run_meta = {"prompt_version": config.version, "model": MODEL, "timestamp": run_path.split("_")[1].split(".")[0]}
    report_path = generate_report(diff, run_meta, history, regressed_cases)
    print(f"Report saved to: {report_path}")

    # 9. Alert if not a clean pass (Slack webhook is optional in local dev, required in CI)
    if "SLACK_WEBHOOK_URL" in __import__("os").environ:
        await send_slack_alert(severity=severity, diff=diff, report_url=report_path)

    # 10. Gate: fail the CI job on critical regressions (Step 19 wires this into branch protection)
    if severity == "critical":
        print("CRITICAL regression detected — failing CI job to block merge.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())