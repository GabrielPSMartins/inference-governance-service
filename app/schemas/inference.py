from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4


class InferenceRequest(BaseModel):
    """Representa o corpo de uma requisição de inferência enviada"""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Texto de entrada enviado pelo usuário para o modelo de IA."
    )
    user_id: UUID = Field(
        ...,
        description="Identificador único do usuário, usado para rastreabilidade e governança."
    )
    max_tokens: Optional[int] = Field(
        default=256,
        ge=1,
        le=1024,
        description="Número máximo de tokens que o modelo pode gerar na resposta."
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.5,
        description="Controla a aleatoriedade da resposta do modelo."
    )


class InferenceResponse(BaseModel):
    """Representa o corpo da resposta devolvida ao cliente após uma inferência bem-sucedida"""

    request_id: UUID = Field(
        default_factory=uuid4,
        description="Identificador único desta requisição, para rastreabilidade e auditoria."
    )
    response: str = Field(
        ...,
        description="Texto gerado pelo modelo de IA em resposta ao prompt."
    )
    model: str = Field(
        ...,
        description="Nome/identificador do modelo que gerou esta resposta."
    )
    input_tokens: int = Field(
        ...,
        ge=0,
        description="Quantidade de tokens consumidos pelo prompt de entrada."
    )
    output_tokens: int = Field(
        ...,
        ge=0,
        description="Quantidade de tokens gerados na resposta pelo modelo."
    )
    latency_ms: float = Field(
        ...,
        ge=0,
        description="Tempo total, em milissegundos, entre o recebimento da requisição e a resposta."
    )
    temperature: float = Field(
        ...,
        description="Temperatura efetivamente utilizada na geração desta resposta."
    )