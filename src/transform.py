import re


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def normalize_result(result: dict) -> dict:
    return {
        "category": normalize_text(result["category"]),
        "summary": normalize_text(result["summary"]),
    }