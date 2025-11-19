"""Example OpenAI provider (no secrets embedded)."""
from __future__ import annotations

from typing import Optional

from openai import OpenAI

from .base import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, *, model: str = "gpt-4o-mini", api_key: Optional[str] = None) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def complete(self, prompt: str, *, temperature: float = 0.2) -> str:
        response = self._client.responses.create(
            model=self._model,
            input=prompt,
            temperature=temperature,
        )
        return response.output[0].content[0].text  # type: ignore[attr-defined]
