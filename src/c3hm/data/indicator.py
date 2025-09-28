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
