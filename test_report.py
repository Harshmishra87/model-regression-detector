import json
from src.report import generate_report

with open("results/scored_v1.json") as f:
    scored_v1 = json.load(f)
with open("results/scored_v2.json") as f:
    scored_v2 = json.load(f)
with open("results/run_20260710T190832Z.json") as f:
    run_v1 = json.load(f)
with open("results/run_20260711T080545Z.json") as f:
    run_v2 = json.load(f)
with open("data/golden_dataset.json") as f:
    dataset = json.load(f)
with open("results/history.json") as f:
    history = json.load(f)

from src.compare import diff_runs
diff = diff_runs(current=scored_v2, previous=scored_v1)

dataset_by_id = {c["id"]: c for c in dataset}
run_v1_by_id = {r["id"]: r for r in run_v1["results"]}
run_v2_by_id = {r["id"]: r for r in run_v2["results"]}

regressed_cases = []
for case_id in diff["regressions"]:
    regressed_cases.append({
        "id": case_id,
        "input": dataset_by_id[case_id]["input"],
        "previous_output": run_v1_by_id[case_id]["output"],
        "current_output": run_v2_by_id[case_id]["output"],
    })

run_meta = {
    "prompt_version": run_v2["prompt_version"],
    "model": run_v2["model"],
    "timestamp": run_v2["timestamp"],
}

path = generate_report(diff, run_meta, history, regressed_cases)
print(f"Report saved to: {path}")