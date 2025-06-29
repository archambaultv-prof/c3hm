from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.rubric.descriptors import Descriptors
from c3hm.data.rubric.format import Format
from c3hm.data.rubric.grade_level import GradeLevel
from c3hm.data.rubric.grade_levels import GradeLevels

CTHM_OMNIVOX = "cthm_omnivox"


class Rubric(BaseModel):
    """
    Représente la grille d'évaluation.

    Une grille est formée de niveaux (Excellent, Très bien, ...) et d'une liste de critères.
    """
    grade_levels: GradeLevels
    evaluation: Evaluation
    format: Format
    descriptors: Descriptors = Field(
        description="Descripteurs pour les critères et indicateurs, "
                    "formatés comme {('niveau.name', 'indicateur.id'): 'descripteur'}."
    )

    @model_validator(mode="after")
    def validate_rubric(self) -> Self:
        """
        Valide la grille d'évaluation.
        """
        # Vérifie la présence de chaque descripteur.
        for criterion in self.evaluation.criteria:
            for indicator in criterion.indicators:
                for level in self.grade_levels.levels:
                    if not self.descriptors.contains(indicator, level):
                        raise ValueError(
                            f"Le descripteur pour l'indicateur '{indicator.name}' "
                            f"du critère '{criterion.name}' au niveau '{level.name}' "
                            "n'est pas défini dans la grille d'évaluation."
                        )

        return self

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant la grille d'évaluation.
        """
        return {
            "niveaux": [gl.to_dict(convert_decimal=convert_decimal)
                        for gl in self.grade_levels.levels],
            "évaluation": self.evaluation.to_dict(convert_decimal=convert_decimal),
            "format": self.format.to_dict(),
            "descripteurs": self.descriptors.to_dict()
        }


    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
        """
        Crée une instance de Rubric à partir d'un dictionnaire.
        """
        levels = [GradeLevel.from_dict(gl) for gl in data["niveaux"]]
        return cls(
            grade_levels=GradeLevels(levels=levels),
            evaluation=Evaluation.from_dict(data["évaluation"]),
            format=Format.from_dict(data["format"]),
            descriptors=Descriptors.from_dict(data["descripteurs"])
        )

    def copy(self) -> "Rubric": # type: ignore
        """
        Retourne une copie de la grille d'évaluation.
        """
        return Rubric(
            grade_levels=self.grade_levels.copy(),
            evaluation=self.evaluation.copy(),
            format=self.format.copy(),
            descriptors=self.descriptors.copy()
        )
