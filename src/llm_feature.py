import json
import os
import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.config import PromptConfig, ClassificationResult

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def load_prompt_config(path: str) -> PromptConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return PromptConfig(**raw)


async def classify_email(
    email_text: str,
    config: PromptConfig,
    model: str = "gemini-2.5-flash",
) -> ClassificationResult:
    # Build few-shot examples as alternating user/model turns
    contents = []
    for ex in config.few_shot_examples:
        contents.append(types.Content(role="user", parts=[types.Part(text=ex["input"])]))
        contents.append(types.Content(role="model", parts=[types.Part(text=ex["output"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=email_text)]))

    response = await client.aio.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=config.system_prompt,
            response_mime_type="application/json",
        ),
    )

    raw_json = json.loads(response.text)
    return ClassificationResult(**raw_json)