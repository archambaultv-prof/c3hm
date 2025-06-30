from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.evaluation.criterion import Criterion
from c3hm.utils.excel import safe_for_named_cell


class Evaluation(BaseModel):
    """
    Information sur une évaluation.
    """
    id: str = Field("eval", min_length=1)
    name: str = Field(..., min_length=1)
    criteria: list[Criterion] = Field(..., min_length=1)
    precision: int = Field(
        0,
        description="Nombre de décimales pour le total de l'évaluation.",
        ge=0,
    )

    def title(self) -> str:
        """
        Retourne le titre de la grille d'évaluation.
        """
        endash = "\u2013"
        title = "Grille d'évaluation"
        title += f" {endash} {self.name}"
        return title

    @model_validator(mode="after")
    def validate_evaluation(self) -> Self:
        """
        Valide que les critères de l'évaluation sont correctement définis.
        """
        if not safe_for_named_cell(self.id):
            raise ValueError(f"L'identifiant '{self.id}' n'est pas valide pour une cellule Excel.")

        # Id unique
        ids = {self.id: 1}
        for criterion in self.criteria:
            ids[criterion.id] = ids.get(criterion.id, 0) + 1
            for indicator in criterion.indicators:
                ids[indicator.id] = ids.get(indicator.id, 0) + 1
        if any(v > 1 for v in ids.values()):
            dups = [id_ for id_, count in ids.items() if count > 1]
            raise ValueError(
                f"Les identifiants de l'évaluation '{self.name}' doivent être uniques. "
                f"Les identifiants suivants sont dupliqués : {', '.join(dups)}."
            )

        return self

    @property
    def points(self) -> Decimal:
        """
        Retourne le nombre total de points de l'évaluation, en sommant les
        points de tous les critères.
        """
        return sum((criterion.points for criterion in self.criteria),
                   start=Decimal(0))

    @property
    def nb_criteria(self) -> int:
        """
        Retourne le nombre de critères dans la grille.
        """
        return len(self.criteria)

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant l'évaluation.
        """
        return {
            "id": self.id,
            "nom": self.name,
            "critères": [criterion.to_dict(convert_decimal)
                         for criterion in self.criteria],
            "précision du total": self.precision
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Evaluation":
        """
        Crée une instance de Evaluation à partir d'un dictionnaire.
        """
        return cls(
            id=data.get("id", "eval"),
            name=data["nom"],
            criteria=[Criterion.from_dict(criterion) for criterion in data["critères"]],
            precision=data.get("précision du total", 0),
        )

    def copy(self) -> "Evaluation": # type: ignore
        """
        Retourne une copie de l'évaluation.
        """
        return Evaluation(
            id=self.id,
            name=self.name,
            criteria=[criterion.copy() for criterion in self.criteria],
            precision=self.precision,
        )
