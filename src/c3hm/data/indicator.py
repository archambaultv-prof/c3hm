from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

NonNegFloat = Annotated[float, Field(ge=0.0)]

class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    points: NonNegFloat | None = Field(None,
                            description="Points associés à cet indicateur.")

    grade: NonNegFloat | str | None = Field(None)
    comment: str | None = Field(None, min_length=1)

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
        if self.grade is None or isinstance(self.grade, str):
            raise ValueError("La note de l'indicateur n'est pas définie.")
        return self.grade
