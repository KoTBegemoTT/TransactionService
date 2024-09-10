import redis
from app.config import settings


class BaseRedisClient:
    """Базовый класс для работы с Redis."""

    def __init__(self, host, port, db_number) -> None:
        self.client = redis.Redis(host=host, port=port, db=db_number)

    def close(self):
        """Закрытие соединения с Redis."""
        self.client.close()

    def set(self, key, value):
        """Установка значения по ключу."""
        self.client.set(key, value)

    def get(self, key):
        """Получение значения по ключу."""
        return self.client.get(key)


class RedisClient(BaseRedisClient):
    """Класс для работы с Redis."""

    def get_transaciton_type_id(self, type_name: str):
        """Получение id типа транзакции."""
        return self.get(f'tt_id:{type_name}')

    def set_transaciton_type_id(self, type_name: str, type_id: int):
        """Установка id типа транзакции."""
        self.set(f'tt_id:{type_name}', type_id)

    def get_report_transaction(self, report_key: str):
        """Получение списка транзакций связанного с отчетом."""
        return self.get(f'report:{report_key}')

    def set_report_transaction(self, report_key: str, value: str):
        """Установка списка транзакций связанного с отчетом."""
        self.set(f'report:{report_key}', value)


redis_client = RedisClient(
    settings.redis_host,
    settings.redis_port,
    settings.redis_db_number,
)


def get_redis_client():
    """Получение экземпляра RedisClient."""
    return redis_client
