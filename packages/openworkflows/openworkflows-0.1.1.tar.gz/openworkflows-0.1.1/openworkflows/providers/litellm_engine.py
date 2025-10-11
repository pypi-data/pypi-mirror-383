from typing import Optional

from litellm import acompletion


class AsyncLiteLLMPCompletion:
    def __init__(self, provider: str, model: str, api_key: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key

    async def __call__(self, prompt: str, system: str, **kwargs) -> str:
        response = await acompletion(
            model=f"{self.provider}/{self.model}",
            api_key=self.api_key,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            **kwargs,
        )
        return response["choices"][0]["message"]["content"]
