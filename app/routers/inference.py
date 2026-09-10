from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.prompt_guard import contains_prompt_injection
from app.services.rate_limiter import is_rate_limited

router = APIRouter(prefix="/inference", tags=["Inference"])


async def validate_rate_limit(payload: InferenceRequest) -> InferenceRequest:
    """
    Verifica se o usuário ultrapassou o limite de
    requisições permitidas na janela de tempo configurada.
    """
    if is_rate_limited(payload.user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de requisições excedido. Tente novamente mais tarde.",
        )
    return payload


async def validate_prompt_security(
    payload: InferenceRequest = Depends(validate_rate_limit),
) -> InferenceRequest:
    """
    Valida o prompt recebido contra a blocklist
    de prompt injection. Executa após a checagem de rate limit.
    """
    if contains_prompt_injection(payload.prompt):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt bloqueado: conteúdo suspeito de manipulação do sistema.",
        )
    return payload


@router.post("", response_model=InferenceResponse)
async def create_inference(
    request: InferenceRequest = Depends(validate_prompt_security),
) -> InferenceResponse:
    """
    Recebe um prompt do cliente e retorna a resposta gerada pelo modelo
    de IA, junto com metadados de observabilidade (tokens, latência,
    modelo utilizado).
    """
    raise NotImplementedError("Camada de Orquestração ainda não implementada")