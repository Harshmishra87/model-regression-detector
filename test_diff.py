import json
from src.compare import diff_runs

with open("results/scored_v1.json") as f:
    v1 = json.load(f)

with open("results/scored_v2.json") as f:
    v2 = json.load(f)

diff = diff_runs(current=v2, previous=v1)
print(json.dumps(diff, indent=2))