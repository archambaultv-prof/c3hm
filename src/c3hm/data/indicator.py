from decimal import Decimal

from pydantic import BaseModel, Field


class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    name: str = Field(..., min_length=1)
    descriptors: list[str]
    weight: Decimal = Field(
        default=Decimal(1),
        description="Poids de l'indicateur dans le critère.",
    )
    xl_cell_id: str | None = Field(
        default=None,
        description="Identifiant de la cellule dans le fichier Excel pour la correction.",
        min_length=1
    )

    def xl_grade_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour la note de l'indicateur.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_grade"

    def xl_comment_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour le commentaire de l'indicateur.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_comment"

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant l'indicateur.
        """
        return {
            "nom": self.name,
            "xl id": self.xl_cell_id,
            "poids": self.weight,
            "descripteurs": self.descriptors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Indicator":
        """
        Crée une instance de Indicator à partir d'un dictionnaire.
        """
        return cls(
            name=data["nom"],
            xl_cell_id=data.get("xl id"),
            weight=data.get("poids", Decimal(1)),
            descriptors=data.get("descripteurs", []),
        )

    def copy(self) -> "Indicator": # type: ignore
        """
        Retourne une copie de l'indicateur.
        """
        return Indicator(
            name=self.name,
            xl_cell_id=self.xl_cell_id,
            weight=self.weight,
            descriptors=self.descriptors.copy(),
        )
