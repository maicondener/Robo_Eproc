from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    EPROC_LOGIN: str
    EPROC_SENHA: str
    EPROC_2FA_SECRET: str = "" # Opcional, para automação de TOTP
    EPROC_URL: str = "https://eproc1.tjto.jus.br/eprocV2_prod_1grau/"
    HEADLESS: bool = True
    BROWSER_CHANNEL: str = "chrome" # chrome, msedge, chrome-beta, etc.
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
