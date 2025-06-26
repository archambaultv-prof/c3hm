from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.rubric.grade_level import GradeLevel


class GradeLevels(BaseModel):
    """
    Représente les niveaux de notes d'une grille d'évaluation.
    """
    levels: list[GradeLevel] = Field(..., min_length=1, description="Liste des niveaux de notes")

    @model_validator(mode="after")
    def validate_graded_levels(self) -> Self:
        # Vérifie que les niveaux de notes sont correctement ordonnés
        limit = self.levels[0].min_percentage
        for level in self.levels[1:]:
            if level.max_percentage > limit:
                raise ValueError("Les niveaux de notes doivent être ordonnés "
                                 "du plus élevé au plus bas.")
        return self

    def get_level_by_percentage(self, percentage: Decimal) -> GradeLevel:
        """
        Retourne le niveau de note correspondant à une note donnée.
        """
        if not (Decimal(0) <= percentage <= Decimal(100)):
            raise ValueError("Le pourcentage doit être compris entre 0 et 100.")
        for level in self.levels:
            if percentage >= level.min_percentage:
                return level
        return self.levels[-1]  # Retourne le niveau le plus bas si aucun autre ne correspond

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant les niveaux de notes.
        """
        return {
            "niveaux": [level.to_dict(convert_decimal=convert_decimal) for level in self.levels]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GradeLevels":
        """
        Crée une instance de GradeLevels à partir d'un dictionnaire.
        """
        return cls(
            levels=[GradeLevel.from_dict(level) for level in data["niveaux"]]
        )

    def copy(self) -> "GradeLevels": # type: ignore
        """
        Retourne une copie de l'instance.
        """
        return GradeLevels(levels=[level.copy() for level in self.levels])
