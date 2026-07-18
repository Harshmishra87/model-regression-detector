import json
import shutil
from datetime import datetime, timezone


def save_run(results: list[dict], prompt_config, model: str, dataset_path: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = {
        "timestamp": timestamp,
        "prompt_version": prompt_config.version,
        "model": model,
        "dataset_path": dataset_path,
        "results": results,
    }
    path = f"results/run_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(run, f, indent=2)
    shutil.copy(path, "results/latest.json")
    return path