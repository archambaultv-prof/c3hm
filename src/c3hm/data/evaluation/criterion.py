from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.evaluation.indicator import Indicator
from c3hm.utils.excel import safe_for_named_cell


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    id: str = Field(..., min_length=1, description="Identifiant unique du critère.")
    name: str = Field(..., min_length=1)
    indicators: list[Indicator] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_indicator(self) -> Self:
        # Valide que le critère est correctement défini.
        if not safe_for_named_cell(self.id):
            raise ValueError(f"L'identifiant '{self.id}' n'est pas valide pour une cellule Excel.")

        # Id unique
        ids = {self.id: 1}
        for indicator in self.indicators:
            ids[indicator.id] = ids.get(indicator.id, 0) + 1
        if any(v > 1 for v in ids.values()):
            dups = [id_ for id_, count in ids.items() if count > 1]
            raise ValueError(
                f"Les identifiants des indicateurs du critère '{self.name}' doivent être uniques. "
                f"Les identifiants suivants sont dupliqués : {', '.join(dups)}."
            )

        return self

    @property
    def points(self) -> Decimal:
        """
        Retourne le nombre total de points attribués au critère, en sommant les
        points de tous les indicateurs.
        """
        return sum((indicator.points for indicator in self.indicators),
                   start=Decimal(0))

    @property
    def nb_indicators(self) -> int:
        """
        Retourne le nombre d'indicateurs dans le critère.
        """
        return len(self.indicators)

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant le critère.
        """
        return {
            "id": self.id,
            "critère": self.name,
            "indicateurs": [indicator.to_dict(convert_decimal=convert_decimal)
                            for indicator in self.indicators],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        """
        Crée une instance de Criterion à partir d'un dictionnaire.
        """
        return cls(
            id=data["id"],
            name=data["critère"],
            indicators=[Indicator.from_dict(ind) for ind in data["indicateurs"]],
        )

    def copy(self) -> "Criterion": # type: ignore
        """
        Retourne une copie du critère.
        """
        return Criterion(
            id=self.id,
            name=self.name,
            indicators=[indicator.copy() for indicator in self.indicators],
        )
