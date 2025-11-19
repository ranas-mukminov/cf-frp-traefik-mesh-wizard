"""Deterministic mock provider."""
from __future__ import annotations

from .base import AIProvider


class MockProvider(AIProvider):
    def __init__(self, response: str = "mock-response") -> None:
        self.response = response

    def complete(self, prompt: str, *, temperature: float = 0.2) -> str:  # noqa: ARG002
        return self.response
