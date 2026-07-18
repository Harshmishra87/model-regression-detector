import asyncio
import re
import time

from src.llm_feature import classify_email


async def run_one(case: dict, config, model: str, max_retries: int = 3) -> dict:
    start = time.perf_counter()
    for attempt in range(max_retries):
        try:
            result = await classify_email(case["input"], config, model=model)
            latency_ms = (time.perf_counter() - start) * 1000
            return {"id": case["id"], "output": result.model_dump(), "latency_ms": latency_ms, "error": None}
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                match = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)", error_str)
                wait_s = int(match.group(1)) + 2 if match else (2 ** attempt) * 5
                print(f"  {case['id']}: rate limited, waiting {wait_s}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_s)
                continue
            return {"id": case["id"], "output": None, "latency_ms": None, "error": error_str}
    return {"id": case["id"], "output": None, "latency_ms": None, "error": "Max retries exceeded"}


async def run_evaluation(
    dataset: list[dict],
    config,
    model: str = "gemini-2.5-flash-lite",
    requests_per_minute: int = 10,
) -> list[dict]:
    delay = 60.0 / requests_per_minute + 1.0  # safety margin on top of the raw RPM math
    results = []
    for i, case in enumerate(dataset):
        result = await run_one(case, config, model)
        results.append(result)
        print(f"Completed {i + 1}/{len(dataset)}" + (f" — ERROR: {result['error']}" if result["error"] else ""))
        if i + 1 < len(dataset):
            await asyncio.sleep(delay)
    return results