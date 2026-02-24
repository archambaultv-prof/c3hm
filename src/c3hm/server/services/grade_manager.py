"""
Service pour gérer les overrides de notes (notes ajustées).
"""

from c3hm.data import JSON_KEY_GRADE_OVERRIDE
from c3hm.server.config import (
    CRITERIA_OVERRIDE_KEY,
    RUBRIC_OVERRIDE_KEY,
    UNSET,
    UnsetType,
)


class GradeManager:
    """
    Gère les overrides de notes (notes ajustées) au niveau critère et rubric.

    Logique:
    - Les overrides de critères sont stockés en clé "note ajustée" dans chaque critère
    - L'override de rubric est stocké en clé "note ajustée" au niveau racine
    """

    @staticmethod
    def get_criteria_overrides(payload: dict) -> dict | None:
        """
        Extrait les overrides de critères d'un payload.

        Cherche la clé "criteria_overrides" selon l'API frontend

        Returns:
            Dict avec format {"crit_idx": override_value} ou None
        """
        return payload.get(CRITERIA_OVERRIDE_KEY)

    @staticmethod
    def get_rubric_grade_override(payload: dict) -> float | str | None | UnsetType:
        """
        Extrait l'override de note de rubric d'un payload.

        Cherche la clé "rubric_grade_override" selon l'API frontend

        Returns:
            La valeur d'override, ou UNSET si non fournie
        """
        value = payload.get(RUBRIC_OVERRIDE_KEY)
        return value if value is not None else UNSET

    @staticmethod
    def get_criterion_override(criterion_data: dict) -> float | str | None:
        """
        Extrait l'override de note d'un critère.

        Cherche la clé "note ajustée"
        """
        if JSON_KEY_GRADE_OVERRIDE in criterion_data:
            return criterion_data.get(JSON_KEY_GRADE_OVERRIDE)
        return None

    @staticmethod
    def set_criterion_override(criterion_data: dict, override_value: float | str | None) -> None:
        """
        Définit l'override de note d'un critère.

        Si override_value est None ou "", supprime la clé.
        Sinon, la définit en "note ajustée".
        """
        if override_value is None or override_value == "":
            criterion_data.pop(JSON_KEY_GRADE_OVERRIDE, None)
            return
        criterion_data[JSON_KEY_GRADE_OVERRIDE] = override_value

    @staticmethod
    def set_rubric_override(rubric_data: dict, override_value: float | str | None | UnsetType) -> None:
        """
        Définit l'override de note de rubric.

        Si override_value est None ou "", supprime la clé.
        Sinon, la définit.
        """
        if override_value is None or override_value == "":
            rubric_data.pop(JSON_KEY_GRADE_OVERRIDE, None)
            return
        rubric_data[JSON_KEY_GRADE_OVERRIDE] = override_value
