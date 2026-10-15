from functools import lru_cache
from pathlib import Path
from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[4]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore",
    )

    database_url: str
    secret_key: SecretStr
    hash_algo: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    running_in_docker: bool = False

    @computed_field
    @property
    def db_dsn(self) -> str:
        if self.running_in_docker:
            return self.database_url
        return self.database_url.replace("@db:", "@localhost:")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

settings = get_settings()