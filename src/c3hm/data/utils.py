from typing import Any


def assert_non_empty_string(value: Any, field_name: str) -> None:
    if value is None or not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"Le champ '{field_name}' doit être une chaîne de caractères non vide.")
