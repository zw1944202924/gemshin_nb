
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "AI股票分析助手"
    env: str = "development"
    database_url: str = "sqlite:///./gemshin_nb.db"
    redis_url: str = "redis://localhost:6379/0"
    doubak_api_key: str = ""
    secret_key: str = "default_secret_key"
    access_token_expire_minutes: int = 30
<<<<<<< HEAD
=======
    refresh_token_expire_days: int = 7
>>>>>>> feature/backend-api-enhancement

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

settings = Settings()
