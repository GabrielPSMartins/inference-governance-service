from fastapi import FastAPI

from app.routers import inference

app = FastAPI(
    title="Serviço de Inferência com Camada de Governança",
    description="Microsserviço que atua como intermediário de governança "
                 "entre usuários e provedores de LLM.",
    version="0.1.0",
)

app.include_router(inference.router)