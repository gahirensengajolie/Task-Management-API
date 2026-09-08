from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # SECURITY: never hardcode secrets. This default is only for local dev
    # and MUST be overridden via a .env file or real env vars in any
    # shared/staging/production environment.
    secret_key: str = "dev-only-change-me-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    database_url: str = "sqlite:///./expense.db"

    class Config:
        env_file = ".env"


settings = Settings()
