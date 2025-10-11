"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The prompt text
            system: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream generated text from a prompt.

        Args:
            prompt: The prompt text
            system: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated text
        """
        pass

    @abstractmethod
    async def embed(self, text: str, **kwargs) -> list[float]:
        """Generate embeddings for text.

        Args:
            text: Text to embed
            **kwargs: Additional provider-specific parameters

        Returns:
            Embedding vector
        """
        pass
