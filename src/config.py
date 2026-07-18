from pydantic import BaseModel, field_validator


class PromptConfig(BaseModel):
    version: str
    system_prompt: str
    few_shot_examples: list[dict]


class ClassificationResult(BaseModel):
    category: str
    summary: str

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, v: str) -> str:
        allowed = {"billing", "technical", "account", "general"}
        if v not in allowed:
            raise ValueError(f"Unknown category: {v}")
        return v