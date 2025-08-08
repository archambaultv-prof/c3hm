from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.config.indicator import Indicator


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    model_config = ConfigDict(extra="forbid")

    excel_id: str = Field(...,  min_length=1, description="Identifiant unique du critère.")
    name: str = Field(..., min_length=1)
    points_total: Decimal = Field(..., gt=Decimal("0"),
                                  description="Total des points attribués au critère.")
    indicators: list[Indicator] = Field(..., min_length=1)

    @property
    def points(self) -> Decimal:
        """
        Retourne le total des points du critère.
        Pour compatibilité avec Evaluation et Indicator.
        """
        return self.points_total
