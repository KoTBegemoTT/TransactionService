from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Настройки."""

    # Настройки db
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_host: str = 'host.docker.internal'
    db_port: str = '5432'
    db_table: str = 'credit_card'
    db_url: str = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_table}'  # noqa: E501, WPS221
    db_echo: bool = True


settings = Settings()
