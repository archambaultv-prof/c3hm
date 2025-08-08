from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.user_config.indicator import UserIndicator


class UserCriterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    model_config = ConfigDict(extra="forbid")

    excel_id: str | None = Field(None,  min_length=1, description="Identifiant unique du critère.")
    name: str = Field(..., min_length=1)
    points_total: Decimal | None = Field(None, gt=Decimal("0"),
                                         description="Total des points attribués au critère.")
    indicators: list[UserIndicator] = Field(..., min_length=1)

