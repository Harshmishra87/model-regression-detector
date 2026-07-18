import asyncio
import json
from src.scoring import score_case

async def main():
    with open("data/golden_dataset.json") as f:
        dataset = json.load(f)
    with open("results/latest.json") as f:
        run = json.load(f)

    dataset_by_id = {c["id"]: c for c in dataset}
    scored = []
    delay = 60.0 / 15 + 1.0  # ~5 seconds between judge calls

    for i, result in enumerate(run["results"]):
        case = dataset_by_id[result["id"]]
        score = await score_case(case, result)
        scored.append(score)
        print(f"Scored {i + 1}/{len(run['results'])}")
        if i + 1 < len(run["results"]):
            await asyncio.sleep(delay)

    with open("results/scored_v2.json", "w") as f:
        json.dump(scored, f, indent=2)
    print("Saved to results/scored_v2.json")

asyncio.run(main())