from fastapi import APIRouter

from app.schemas.inference import InferenceRequest, InferenceResponse

router = APIRouter(prefix="/inference", tags=["Inference"])


@router.post("", response_model=InferenceResponse)
async def create_inference(request: InferenceRequest) -> InferenceResponse:
    """
    Recebe um prompt do cliente e retorna a resposta gerada pelo modelo
    de IA, junto com metadados de observabilidade."""
    raise NotImplementedError("Camada de Orquestração ainda não implementada")