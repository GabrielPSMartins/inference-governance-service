from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação, carregadas de variáveis de ambiente
    """

    groq_api_key: str
    groq_model: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """
    Carrega as configurações sob demanda, e não no import do módulo.
    """
    return Settings()
