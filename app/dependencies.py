from functools import lru_cache

from app.core.config import get_settings
from app.providers.base import LLMProvider
from app.providers.groq import GroqProvider


@lru_cache
def get_provider() -> LLMProvider:
    """
    Fornece o provedor de LLM às rotas via Depends.
    """
    settings = get_settings()
    return GroqProvider(model=settings.groq_model, api_key=settings.groq_api_key)
