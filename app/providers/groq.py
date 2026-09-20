from groq import AsyncGroq

from app.providers.base import ProviderResponse

MAX_RETRIES = 3


class GroqProvider:
    """
    Implementação concreta de LLMProvider (ADR-0002) usando a API do
    Groq, via biblioteca oficial `groq`.
    """

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._client = AsyncGroq(api_key=api_key, max_retries=MAX_RETRIES)

    async def generate(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        completion = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return ProviderResponse(
            text=completion.choices[0].message.content,
            model=self._model,
            input_tokens=completion.usage.prompt_tokens,
            output_tokens=completion.usage.completion_tokens,
        )