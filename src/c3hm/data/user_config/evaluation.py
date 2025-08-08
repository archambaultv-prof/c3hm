from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.config.grade_level import GradeLevel
from c3hm.data.user_config.criterion import UserCriterion


class UserEvaluation(BaseModel):
    """
    Information sur une évaluation.
    """
    model_config = ConfigDict(extra="forbid")

    excel_id: str = "eval"
    name: str = Field(..., min_length=1)
    points_inference_step: Decimal = Decimal("1")
    points_total: Decimal | None = Field(None, gt=Decimal("0"))
    points_total_nb_of_decimal: int = 0
    grade_levels: list[GradeLevel] = Field(..., min_length=1)
    criteria: list[UserCriterion] = Field(..., min_length=1)
