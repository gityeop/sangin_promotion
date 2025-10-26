from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("Sangin Promotion Quiz", env="APP_NAME")
    secret_key: str = Field("super-secret-key", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field("sqlite:///./quiz.db", env="DATABASE_URL")
    admin_username: str = Field("admin", env="ADMIN_USERNAME")
    admin_password: str = Field("admin123", env="ADMIN_PASSWORD")
    default_passing_score: int = Field(70, env="DEFAULT_PASSING_SCORE")
    default_num_questions: int = Field(10, env="DEFAULT_NUM_QUESTIONS")
    default_num_options: int = Field(10, env="DEFAULT_NUM_OPTIONS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
