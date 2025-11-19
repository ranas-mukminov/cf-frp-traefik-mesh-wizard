"""Abstract AI provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class AIProvider(ABC):
    """Minimal wrapper to abstract LLM vendors."""

    @abstractmethod
    def complete(self, prompt: str, *, temperature: float = 0.2) -> str:
        """Return completion text for prompt."""


class ProviderRegistry:
    """Simple registry so tests can swap implementations."""

    def __init__(self) -> None:
        self._provider: AIProvider | None = None

    def configure(self, provider: AIProvider) -> None:
        self._provider = provider

    def require(self) -> AIProvider:
        if not self._provider:
            raise RuntimeError("AI provider not configured")
        return self._provider


registry = ProviderRegistry()
