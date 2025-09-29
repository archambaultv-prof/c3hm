from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.indicator import Indicator


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernier est formé d'une liste d'indicateurs.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    total: float | None = Field(..., gt=0.0)

    grade: float | None = Field(..., ge=0.0)
    comment: str | None = Field(..., min_length=1)

    indicators: list[Indicator] = Field(..., min_length=1)

    def get_total(self) -> float:
        """
        Retourne le total des points de l'évaluation.
        """
        if self.total is None:
            raise ValueError("Le total des points du critère n'est pas défini.")
        return self.total

    def get_grade(self) -> float:
        """
        Retourne la note du critère.
        """
        if self.grade is None:
            raise ValueError("La note du critère n'est pas définie.")
        return self.grade
