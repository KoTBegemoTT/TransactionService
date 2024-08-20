from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки."""

    # Настройки db
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_host: str = 'host.docker.internal'
    db_port: str = '5432'
    db_name: str = 'credit_card'
    db_url: str = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'  # noqa: E501, WPS221
    db_echo: bool = True

    @property
    def db_url(self) -> str:
        """Ссылка на БД."""
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'  # noqa: E501, WPS221


settings = Settings()
