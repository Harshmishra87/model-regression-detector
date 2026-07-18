import asyncio
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.transform import normalize_text

load_dotenv()
judge_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def category_score(predicted: str, expected: str) -> int:
    return int(normalize_text(predicted) == normalize_text(expected))


async def quality_score(email: str, predicted_summary: str, expected_summary: str, max_retries: int = 3) -> int:
    prompt = (
        f"Email: {email}\nExpected summary: {expected_summary}\n"
        f"Candidate summary: {predicted_summary}\n"
        "Rate the candidate summary's accuracy and usefulness from 1 (poor) to 5 (excellent). "
        "Respond with ONLY the number."
    )
    for attempt in range(max_retries):
        try:
            response = await judge_client.aio.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
            )
            return int(response.text.strip())
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                match = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)", error_str)
                wait_s = int(match.group(1)) + 2 if match else (2 ** attempt) * 5
                print(f"    rate limited, waiting {wait_s}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_s)
                continue
            raise
    raise RuntimeError("Max retries exceeded for quality_score")


async def score_case(case: dict, run_result: dict) -> dict:
    output = run_result["output"] or {}

    if run_result["error"]:
        return {
            "id": case["id"],
            "category_score": 0,
            "quality_score": 0,
            "latency_ms": run_result["latency_ms"],
            "error": run_result["error"],
        }

    return {
        "id": case["id"],
        "category_score": category_score(output.get("category", ""), case["expected_category"]),
        "quality_score": await quality_score(case["input"], output.get("summary", ""), case["expected_summary"]),
        "latency_ms": run_result["latency_ms"],
        "error": None,
    }