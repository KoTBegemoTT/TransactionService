# TransactionService

Позволяет пользователям совершать транзакции, а также получить информацию о транзакциях в определённо промежутке.

Этот сервис является частью группы микросервисов, входной точкой для которых является [ApiGateway](https://hub.mos.ru/shift-python/y2024/homeworks/plebedev/api-gateway)

# REST API

`POST /api/create/`

- Создаёт транзакцию.

`POST /api/report/`

- Генерирует и сохраняет отчёт о транзакциях в определённом промежутке. В случае успеха возвращает список транзакций.

## Инструкция по запуску

### Перед началом

* Установить docker

### Запуск

```bash
docker compose build
docker compose up
```

### Важные эндпоинты *
* [http://localhost:8002/docs](http://localhost:8002/docs) - Transaction

* [http://localhost:16686](http://localhost:16686) - Веб интерфейс Jaeger

## Развёртывание в kubernetes

### Порядок развёртывания

1. Transaction
2. Auth
3. Face-Verification
4. ApiGateway

### Продакшен

```bash
cd helm/lebedev-transaction
helm install my-release-name .
```

### Тестирование

```bash
cd helm/lebedev-transaction
helm install my-release-name --values ./values/test.yaml
```