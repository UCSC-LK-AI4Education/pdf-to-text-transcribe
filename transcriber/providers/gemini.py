"""
A concrete provider that's using Google Gemini API
"""

from google import genai
from google.genai import types
from pydantic import BaseModel


class GeminiProvider:
    def __init__(self, model: str, api_key: str, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        self.client = genai.Client(api_key=api_key)

    def transcribe(self, pages, system, prompt, item_model: type[BaseModel]) -> list[dict]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=[*pages, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_schema=list[item_model],
                temperature=self.temperature,
            ),
        )
        if response.parsed is None:
            preview = (response.text or "")[:200]
            raise RuntimeError(f"Model output could not be parsed: {preview!r}")
        return [item.model_dump() for item in response.parsed]