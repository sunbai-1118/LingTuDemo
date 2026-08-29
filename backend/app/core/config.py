from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "LingTuDemo API"
    debug: bool = False

    # Database
    database_url: str = "mysql+pymysql://lingtu:lingtu123@localhost:3306/lingtu?charset=utf8mb4"

    # JWT
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    # LLM moderation
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 15

    # Seeded admin account for Resource B testing
    admin_username: str = "admin"
    admin_password: str = "admin12345"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
