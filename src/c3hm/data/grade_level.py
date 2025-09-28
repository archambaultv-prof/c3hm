from pydantic import BaseModel, ConfigDict, Field


class GradeLevel(BaseModel):
    """
    Représente un niveau de note comme Excellent, Bon, Passable, Insuffisant.
    Les seuils sont exprimés en pourcentage et doivent être compris entre 0 et 1.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    maximum: float = Field(
        ...,
        description="Valeur maximale de la note pour ce niveau",
        gt=0.0,
        le=100.0,
    )
    minimum: float = Field(
        ...,
        description="Valeur minimale de la note pour ce niveau",
        ge=0.0,
        lt=100.0,
    )
    default_value: float = Field(
        ...,
        description="Valeur par défaut de la note pour ce niveau",
        ge=0.0,
        le=100.0,
    )

    def level_description(self) -> str:
        """
        Retourne une chaîne de caractères représentant le niveau
        """
        if self.minimum == self.maximum:
            return f"{self.minimum:.0f}%"
        else:
            if self.minimum == 0:
                return f"{self.maximum:.0f}% et moins"
            return f"{self.maximum:.0f}% à {self.minimum:.0f}%"
