from pydantic import BaseModel, ConfigDict, Field


class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    points: float | None = Field(..., gt=0.0,
                            description="Points associés à cet indicateur.")

    grade: float | None = Field(..., ge=0.0)
    comment: str | None = Field(..., min_length=1)

    descriptors: list[str | None] = Field(
        ...,
        min_length=1,
        description="Liste des descripteurs associés à cet indicateur."
    )

    def get_total(self) -> float:
        """
        Retourne le total des points de l'indicateur.
        """
        if self.points is None:
            raise ValueError("Le total des points de l'indicateur n'est pas défini.")
        return self.points

    def get_grade(self) -> float:
        """
        Retourne la note de l'indicateur.
        """
        if self.grade is None:
            raise ValueError("La note de l'indicateur n'est pas définie.")
        return self.grade
