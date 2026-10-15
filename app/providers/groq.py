import groq
from groq import AsyncGroq

from app.providers.base import ProviderResponse
from app.providers.errors import (
    ProviderError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

MAX_RETRIES = 3
TIMEOUT_SECONDS = 20.0


class GroqProvider:
    """
    Implementação concreta de LLMProvider (ADR-0002) usando a API do
    Groq, via biblioteca oficial `groq`.
    """

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._client = AsyncGroq(
            api_key=api_key,
            max_retries=MAX_RETRIES,
            timeout=TIMEOUT_SECONDS,
        )

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

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except groq.APIError as exc:
            raise _translate_error(exc) from exc

        choice = completion.choices[0]
        usage = completion.usage
        details = usage.completion_tokens_details

        return ProviderResponse(
            text=choice.message.content,
            model=completion.model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            finish_reason=choice.finish_reason,
            reasoning_tokens=details.reasoning_tokens if details else None,
        )


def _translate_error(exc: groq.APIError) -> ProviderError:
    error_type = type(exc).__name__
    status_code = getattr(exc, "status_code", None)

    if isinstance(exc, groq.APITimeoutError):
        return ProviderTimeoutError(str(exc), error_type=error_type)
    if isinstance(exc, groq.APIConnectionError):
        return ProviderUnavailableError(str(exc), error_type=error_type)
    if isinstance(exc, groq.RateLimitError) or status_code == 503:
        return ProviderUnavailableError(
            str(exc), error_type=error_type, upstream_status_code=status_code
        )
    return ProviderError(str(exc), error_type=error_type, upstream_status_code=status_code)
