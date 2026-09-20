from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação, carregadas de variáveis de ambiente
    """

    groq_api_key: str
    groq_model: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()