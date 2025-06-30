from pydantic import BaseModel, Field

from c3hm.data.evaluation.indicator import Indicator
from c3hm.data.rubric.grade_level import GradeLevel


class Descriptors(BaseModel):
    """
    Classe représentant les descripteurs d'une grille d'évaluation.
    """
    descriptors:  dict[tuple[str, str], str] = Field(
        ...,
        description="Descripteurs pour les critères et indicateurs, "
                    "formatés comme {('niveau.name', 'indicateur.id'): 'descripteur'}."
    )

    def contains(self, indicator: Indicator, level: GradeLevel) -> bool:
        """
        Vérifie si un descripteur existe pour un indicateur et un niveau donnés.
        """
        return (indicator.id, level.name) in self.descriptors

    def get_descriptor(self, indicator: Indicator, level: GradeLevel,) -> str:
        """
        Retourne le descripteur pour un niveau et un indicateur donnés.
        """
        return self.descriptors[(indicator.id, level.name)]

    def set_descriptor(self, indicator: Indicator, level: GradeLevel, descriptor: str) -> None:
        """
        Définit le descripteur pour un niveau et un indicateur donnés.
        """
        self.descriptors[(indicator.id, level.name)] = descriptor

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant les descripteurs.
        """
        return self.descriptors

    @classmethod
    def from_dict(cls, data: dict) -> "Descriptors":
        """
        Crée une instance de Descriptors à partir d'un dictionnaire.
        """
        return cls(descriptors=data)

    def copy(self) -> "Descriptors":  # type: ignore
        """
        Retourne une copie des descripteurs.
        """
        return Descriptors(descriptors=self.descriptors.copy())
