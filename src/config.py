from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    EPROC_LOGIN: str
    EPROC_SENHA: str
    EPROC_URL: str = "https://eproc1.tjto.jus.br/eprocV2_prod_1grau/"
    EPROC_2FA_SECRET: Optional[str] = None
    EPROC_PERFIL: Optional[str] = None # Perfil de usuário (ex: DIRETOR DE SECRETARIA)
    
    # Configurações do Navegador
    HEADLESS: bool = True
    BROWSER_CHANNEL: str = "chrome" # chrome, msedge, chromium
    LOG_LEVEL: str = "INFO"

    # Integração LegalMind Core
    LEGALMIND_API_URL: str = "http://localhost:8000/api/v1/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
