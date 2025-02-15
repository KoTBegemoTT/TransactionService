# Changelog

Все заметные изменения в этом проекте будут задокументированы в этом файле.

Этот формат основывается на [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), и этот проект придерживается [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.0] - 2024-09-10

### Добавлено
- Добавлен докерфайл для запуска сервиса с зависимостями

### Изменено:

- Кеш теперь хранится в редис

## [4.0.0] - 2024-09-06

### Добавлено

- Трейсинг с jaeger

### Изменено

- url серивиса теперь начинаются с префикса "api/"

## [3.1.0] - 2024-08-29

### Добавлено

- Helm чарты

## [3.0.0] - 2024-08-27

### Добавлено

- Манифесты для запуска приложения в kubernetes

### Изменено:

- При миграции таблицы создаются в схеме lebedev_schema

## [2.0.0] - 2024-08-19

### Добавлено

- Миграции с alembic
- Подключение к тестовой бд во время тестов.
- Инструкция по миграциям в contributing.

### Изменено

- Данные о пользователях теперь хранятся в postgres.
- Обновлены тесты для проверки сохранения данных в бд.
- Модели, которые раньше были реализованы через датаклассы, теперь реализованы с помощью sqlalchemy.

## [1.2.0] - 2024-08-3

### Добавлено

- url /healthz/ready/ для проверки состояния сервиса. Возвращает статус OK(200)

### Изменено

- Теперь при запросе отчёта о транзакциях сервис сначала проверяет не был ли уже выполнен отчёт с такими же датами и возвращает существующий если он есть.

## [1.1.0] - 2024-08-1

### Добавлено

- Docker контейнер

## [1.0.0] - 2024-07-28

### Добавлено

- Api с использованием FastApi

## [0.1.0] - 2024-07-15

### Добавлено

- Класс транзакций, с возможностями создать и получить транзакцию.
- Тесты с pytest
- gitlab-ci
