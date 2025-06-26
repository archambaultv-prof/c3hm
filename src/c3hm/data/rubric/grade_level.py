from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.utils.decimal import decimal_to_number


class GradeLevel(BaseModel):
    """
    Représente un niveau de note comme Excellent, Bon, Passable, Insuffisant.
    Les seuils sont exprimés en pourcentage et doivent être compris entre 0 et 100.
    """
    name: str = Field(..., min_length=1)
    max_percentage: Decimal = Field(
        ...,
        description="Valeur maximale de la note pour ce niveau",
        gt=Decimal(0),
        le=Decimal("100"),
    )
    min_percentage: Decimal = Field(
        ...,
        description="Valeur minimale de la note pour ce niveau",
        ge=Decimal(0),
        lt=Decimal("100"),
    )

    @model_validator(mode="after")
    def validate_graded_level(self) -> Self:
        """
        Valide que le niveau de note est correctement défini.
        """
        if self.min_percentage > self.max_percentage:
            raise ValueError("La valeur minimale ne peut pas être supérieure"
                             " à la valeur maximale.")
        return self

    def level_description(self) -> str:
        """
        Retourne une chaîne de caractères représentant le niveau
        """
        if self.min_percentage == self.max_percentage:
            return f"{self.min_percentage}"
        else:
            if self.min_percentage == Decimal("0"):
                return f"{self.max_percentage} et moins"
            return f"{self.max_percentage} à {self.min_percentage}"

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Convertit l'objet en dictionnaire.
        """
        return {
            "nom": self.name,
            "maximum": (self.max_percentage
                        if not convert_decimal
                        else decimal_to_number(self.max_percentage)),
            "minimum": (self.min_percentage
                        if not convert_decimal
                        else decimal_to_number(self.min_percentage)),
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Crée une instance de GradeLevel à partir d'un dictionnaire.
        """
        return cls(
            name=data["nom"],
            max_percentage=data["maximum"],
            min_percentage=data["minimum"],
        )

    def copy(self) -> "GradeLevel":  # type: ignore
        """
        Retourne une copie de l'instance GradeLevel.
        """
        return GradeLevel(
            name=self.name,
            max_percentage=self.max_percentage,
            min_percentage=self.min_percentage,
        )
