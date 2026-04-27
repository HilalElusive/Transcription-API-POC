from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", )

    openai_api_key: str
    openai_model: str = "gpt-5-mini"

    log_level: str = "INFO"
    
    aws_region: str = "eu-west-3"

    database_url: str = "postgresql+psycopg://transcription:transcription@postgres:5432/transcription"
    db_pool_size: int = 5
    db_max_overflow: int = 10


settings = Settings()