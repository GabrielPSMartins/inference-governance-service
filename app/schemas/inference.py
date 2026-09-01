from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class InferenceRequest(BaseModel):
    """
    Representa o corpo de uma requisição de inferência enviada
    pelo cliente.
    """

    #TODO: Adicionar uma camada de autenticação.

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