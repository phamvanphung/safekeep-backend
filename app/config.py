from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # SMTP / email settings
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True  # STARTTLS

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
