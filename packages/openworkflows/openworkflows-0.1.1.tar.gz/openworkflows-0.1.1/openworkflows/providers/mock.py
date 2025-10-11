"""Mock LLM provider for testing."""

from typing import Optional, AsyncIterator

from openworkflows.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider that returns predefined responses."""

    def __init__(self, response: str = "Mock LLM response"):
        """Initialize mock provider.

        Args:
            response: The response to return for all generations
        """
        self.response = response
        self.call_count = 0
        self.last_prompt = None
        self.last_system = None

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Return mock response.

        Args:
            prompt: The prompt text
            system: Optional system message
            temperature: Sampling temperature (ignored)
            max_tokens: Maximum tokens (ignored)
            **kwargs: Additional parameters (ignored)

        Returns:
            Mock response
        """
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system = system
        return self.response

    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream mock response word by word.

        Args:
            prompt: The prompt text
            system: Optional system message
            temperature: Sampling temperature (ignored)
            max_tokens: Maximum tokens (ignored)
            **kwargs: Additional parameters (ignored)

        Yields:
            Words from mock response
        """
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system = system

        words = self.response.split()
        for word in words:
            yield word + " "

    async def embed(self, text: str, **kwargs) -> list[float]:
        """Return mock embedding.

        Args:
            text: Text to embed
            **kwargs: Additional parameters (ignored)

        Returns:
            Mock embedding vector
        """
        # Return a simple mock embedding based on text length
        return [float(len(text)) / 100.0] * 384  # Common embedding size
