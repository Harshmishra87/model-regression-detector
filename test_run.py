import asyncio
import json
from src.llm_feature import load_prompt_config, classify_email
from src.runner import run_evaluation
from src.persistence import save_run

async def main():
    config = load_prompt_config("prompts/email_classifier_v2.yaml")
    with open("data/golden_dataset.json") as f:
        dataset = json.load(f)

    results = await run_evaluation(dataset, config, model="gemini-3.1-flash-lite", requests_per_minute=15)
    print(f"Ran {len(results)} cases")
    print(f"Errors: {sum(1 for r in results if r['error'])}")

    path = save_run(results, config, model="gemini-3.1-flash-lite", dataset_path="data/golden_dataset.json")
    print(f"Saved to: {path}")

asyncio.run(main())