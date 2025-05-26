from decimal import Decimal

from pydantic import BaseModel, Field

from c3hm.data.indicator import Indicator
from c3hm.utils.decimal import decimal_to_number


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    name: str = Field(..., min_length=1)
    percentage: Decimal | None = Field(..., gt=Decimal(0))
    indicators: list[Indicator] = Field(..., min_length=1)
    xl_cell_id: str | None = Field(
        default=None,
        description="Identifiant de la cellule dans le fichier Excel pour la correction.",
        min_length=1
    )

    def xl_grade_overwrite_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour la note du critère
        losque la note est écrasée manuellement.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_grade_overwrite"

    def xl_comment_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour le commentaire du critère.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_comment"

    def nb_indicators(self) -> int:
        """
        Retourne le nombre d'indicateurs dans le critère.
        """
        return len(self.indicators)

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le critère.
        """
        return {
            "critère": self.name,
            "xl id": self.xl_cell_id,
            "indicateurs": [indicator.to_dict() for indicator in self.indicators],
            "pourcentage": decimal_to_number(self.percentage) if self.percentage else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        """
        Crée une instance de Criterion à partir d'un dictionnaire.
        """
        return cls(
            name=data["critère"],
            percentage=data.get("pourcentage"),
            indicators=[Indicator.from_dict(ind) for ind in data["indicateurs"]],
            xl_cell_id=data.get("xl id"),
        )

    def copy(self) -> "Criterion": # type: ignore
        """
        Retourne une copie du critère.
        """

        return Criterion(
            name=self.name,
            xl_cell_id=self.xl_cell_id,
            percentage=self.percentage,
            indicators=[indicator.copy() for indicator in self.indicators],
        )
