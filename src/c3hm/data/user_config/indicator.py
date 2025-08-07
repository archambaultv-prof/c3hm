from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class UserIndicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    model_config = ConfigDict(extra="forbid")

    excel_id: str | None = Field(None, min_length=1,
                                 description="Identifiant unique de l'indicateur.")
    name: str = Field(..., min_length=1)
    points: Decimal | None = Field(None, gt=Decimal("0"),
                                   description="Points associés à cet indicateur.")
    descriptors: list[str | None] = Field(
        ...,
        min_length=1,
        description="Liste des descripteurs associés à cet indicateur."
    )
