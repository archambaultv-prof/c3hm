from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.utils.decimal import decimal_to_number
from c3hm.utils.excel import safe_for_named_cell


class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    id: str = Field(..., min_length=1, description="Identifiant unique de l'indicateur.")
    name: str = Field(..., min_length=1)
    points: Decimal = Field(
        ...,
        description="Nombre de points attribués à cet indicateur.",
        gt=Decimal("0"),
    )


    @model_validator(mode="after")
    def validate_indicator(self) -> Self:
        if not safe_for_named_cell(self.id):
            raise ValueError(f"L'identifiant '{self.id}' n'est pas valide pour une cellule Excel.")

        return self

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant l'indicateur.
        """
        pts = self.points if not convert_decimal else decimal_to_number(self.points)
        return {
            "id": self.id,
            "indicateur": self.name,
            "points": pts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Indicator":
        """
        Crée une instance de Indicator à partir d'un dictionnaire.
        """
        return cls(
            id=data["id"],
            name=data["indicateur"],
            points=data["points"],
        )

    def copy(self) -> "Indicator": # type: ignore
        """
        Retourne une copie de l'indicateur.
        """
        return Indicator(
            id=self.id,
            name=self.name,
            points=self.points,
        )
