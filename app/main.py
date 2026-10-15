from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.providers.errors import ProviderError
from app.routers import inference

configure_logging()

app = FastAPI(
    title="Serviço de Inferência com Camada de Governança",
    description="Microsserviço que atua como intermediário de governança "
                 "entre usuários e provedores de LLM.",
    version="0.1.0",
)

app.add_middleware(RequestContextMiddleware)
app.include_router(inference.router)


@app.exception_handler(ProviderError)
async def handle_provider_error(request: Request, exc: ProviderError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.public_message},
    )
