from pydantic import BaseSettings, Field, ValidationError

class EnvSettings(BaseSettings):
    GOOGLE_API_KEY: str = Field(
        ...,
        description="Chave da API do Google Gemini para acesso ao modelo Gemini.",
    )

try:
    env_settings = EnvSettings()
except ValidationError as e:
    raise Exception(f"Erro nas variáveis de ambiente: {e}")

# Exporta as variáveis validadas
GOOGLE_API_KEY = env_settings.GOOGLE_API_KEY