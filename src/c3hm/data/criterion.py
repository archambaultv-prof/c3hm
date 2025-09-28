from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.indicator import Indicator


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    total: float | None = Field(..., gt=0.0)

    grade: float | None = Field(..., ge=0.0)
    comment: str | None = Field(..., min_length=1)

    indicators: list[Indicator] = Field(..., min_length=1)

