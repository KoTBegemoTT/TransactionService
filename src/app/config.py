from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки."""

    # Общие настройки
    service_name: str = 'transaction-service'

    # Настройки db
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_host: str = 'host.docker.internal'
    db_port: str = '5432'
    db_name: str = 'credit_card'
    db_echo: bool = False
    db_schema: str = 'lebedev_schema'

    # Настройки Jaeger
    jaeger_agent_host: str = 'host.docker.internal'
    jaeger_agent_port: str = '6831'
    jaeger_sampler_type: str = 'const'
    jaeger_sampler_param: float = 1.0
    jaeger_logging: bool = True
    jaeger_validate: bool = True

    @property
    def db_url(self) -> str:
        """Ссылка на БД."""
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'  # noqa: E501, WPS221


settings = Settings()
