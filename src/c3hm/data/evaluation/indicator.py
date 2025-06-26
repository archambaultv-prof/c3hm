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
    description: str = Field(..., min_length=1)
    points: Decimal = Field(
        ...,
        description="Nombre de points attribués à cet indicateur.",
        ge=Decimal(0),  #  Zéro permis pour donner la possibilité de ne pas évaluer un indicateur
    )
    grade: Decimal | None = Field(..., ge=Decimal(0))
    comment: str

    @property
    def has_grade(self) -> bool:
        """
        Indique si l'évaluation est notée.
        """
        return self.grade is not None

    @model_validator(mode="after")
    def validate_indicator(self) -> Self:
        if not safe_for_named_cell(self.id):
            raise ValueError(f"L'identifiant '{self.id}' n'est pas valide pour une cellule Excel.")
        if self.has_grade:
            if self.grade > self.points: # type: ignore
                raise ValueError(
                    f"La valeur de la note ({self.grade}) ne peut pas dépasser "
                    f"le nombre de points attribués à l'indicateur ({self.points})."
                )
        else:
            if self.comment:
                raise ValueError(
                    "Un indicateur sans note ne peut pas avoir de commentaire."
                )
        self.comment = self.comment.strip()
        return self

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant l'indicateur.
        """
        pts = self.points if not convert_decimal else decimal_to_number(self.points)
        if self.has_grade:
            grade = decimal_to_number(self.grade) if convert_decimal else self.grade # type: ignore
        else:
            grade = None
        return {
            "id": self.id,
            "description": self.description,
            "points": pts,
            "note": grade,
            "commentaire": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Indicator":
        """
        Crée une instance de Indicator à partir d'un dictionnaire.
        """
        return cls(
            id=data["id"],
            description=data["description"],
            points=data["points"],
            grade=data.get("note"),  # type: ignore
            comment=data.get("commentaire", ""),
        )

    def copy(self) -> "Indicator": # type: ignore
        """
        Retourne une copie de l'indicateur.
        """
        return Indicator(
            id=self.id,
            description=self.description,
            points=self.points,
            grade=self.grade,  # type: ignore
            comment=self.comment
        )
