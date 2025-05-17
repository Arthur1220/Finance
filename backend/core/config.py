import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class EnvSettings(BaseSettings):
    # Agora aceitamos None sem estourar ValidationError
    GOOGLE_API_KEY: Optional[str] = Field(
        None,
        description="Chave da API do Google Gemini."
    )

# Carrega sem exception
env_settings = EnvSettings()

# Use primeiro o valor do Pydantic, se existir;
# caso contrário, caia em os.environ (para suportar export via shell ou .env)
GOOGLE_API_KEY = (
    env_settings.GOOGLE_API_KEY
    or os.getenv('GOOGLE_API_KEY')
)