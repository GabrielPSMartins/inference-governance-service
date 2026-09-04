from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.prompt_guard import contains_prompt_injection

router = APIRouter(prefix="/inference", tags=["Inference"])


async def validate_prompt_security(payload: InferenceRequest) -> InferenceRequest:
    """
    Dependency do FastAPI: valida o prompt recebido contra a blocklist
    de prompt injection antes da requisição chegar à função da rota.
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
    de IA, junto com metadados de observabilidade 
    """
    raise NotImplementedError("Camada de Orquestração ainda não implementada")