from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProviderResponse:
    """
    Representa o resultado bruto de uma chamada a um provedor de LLM,
    antes de ser formatado como InferenceResponse.
    """
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMProvider(Protocol):
    """
    Contrato que qualquer provedor de LLM deve implementar (ADR-0002).
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        ...