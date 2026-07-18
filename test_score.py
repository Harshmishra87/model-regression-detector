import asyncio
import json
from src.scoring import score_case

async def main():
    with open("data/golden_dataset.json") as f:
        dataset = json.load(f)
    with open("results/latest.json") as f:
        run = json.load(f)

    case = dataset[0]
    run_result = run["results"][0]
    score = await score_case(case, run_result)
    print(score)

asyncio.run(main())