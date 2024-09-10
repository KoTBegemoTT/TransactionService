import json  # noqa: WPS100


def json_nested_load(seq: str) -> list:
    """Восстановление вложенной json структуры из строки."""
    first_level = json.loads(seq)
    second_level = [json.loads(model) for model in first_level]
    return second_level


def json_nested_dump(seq: list) -> str:
    """Запись вложенной json структуры в строку."""
    first_level = [model.model_dump_json() for model in seq]
    return json.dumps(first_level)
