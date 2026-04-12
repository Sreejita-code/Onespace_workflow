from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_uri: str
    mongodb_db: str = "workflow_builder"
    openai_api_key: str
    openai_model: str = "gpt-4o"
    jwt_secret: str
    jwt_expires_minutes: int = 15
    refresh_token_days: int = 7
    env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()