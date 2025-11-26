from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    EPROC_LOGIN: str
    EPROC_SENHA: str
    HEADLESS: bool = True
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
