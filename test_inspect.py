import json

with open("results/run_20260710T190832Z.json") as f:
    v1 = json.load(f)

with open("results/run_20260711T080545Z.json") as f:
    v2 = json.load(f)

v1_by_id = {r["id"]: r for r in v1["results"]}
v2_by_id = {r["id"]: r for r in v2["results"]}

for case_id in ["case_020", "case_096"]:
    print(f"--- {case_id} ---")
    print("v1:", v1_by_id[case_id]["output"])
    print("v2:", v2_by_id[case_id]["output"])
    print()