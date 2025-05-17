import os
from google import genai
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException
from health_check.plugins import plugin_dir 
from .config import env_settings

class GeminiHealthCheck(BaseHealthCheckBackend):
    """Verifica se conseguimos conversar com a API Google Gemini."""
    def check_status(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise HealthCheckException("GOOGLE_API_KEY não está definido")
        try:
            client = genai.Client(api_key=api_key)
            # chamada leve: lista apenas 1 modelo
            models = client.models.list()
            if not models:
                # se a lista vier vazia, OK também, mas você pode opcionalmente checar conteúdo
                return
        except Exception as e:
            raise HealthCheckException(f"Erro conectando ao Gemini: {e!r}")

    def identifier(self):
        return "Google Gemini API"
    
plugin_dir.register(GeminiHealthCheck)