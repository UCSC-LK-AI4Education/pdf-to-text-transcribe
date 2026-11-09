"""
File contains the shape of a LLM provider required for the transcriber.
Each Provider must have the transcribe function and the implementation can differ as one requires.
"""

from typing import Protocol
from PIL import Image
from pydantic import BaseModel


class Provider(Protocol):
    def transcribe(self, pages: list[Image.Image], system: str, prompt: str,
                   item_model: type[BaseModel]) -> list[dict]: ...