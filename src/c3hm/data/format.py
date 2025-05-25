from typing import Literal

from pydantic import BaseModel, Field


class Format(BaseModel):
    """
    Représente le format de la grille d'évaluation.
    """
    orientation: None | Literal["portrait", "paysage"] = Field(
        default=None,
        description="Orientation de la grille d'évaluation. Peut être 'portrait' ou 'paysage'."
    )
    show_indicators_pts: bool = Field(
        default=True,
        description="Indique si le poids des indicateurs doit être affiché."
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le format de la grille d'évaluation.
        """
        return {
            "orientation": self.orientation,
            "afficher la pondération des indicateurs": self.show_indicators_pts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Format":
        """
        Crée une instance de Format à partir d'un dictionnaire.
        """
        return cls(
            orientation=data.get("orientation"),
            show_indicators_pts=data.get("afficher la pondération des indicateurs", True),
        )

    def copy(self) -> "Format": # type: ignore
        """
        Retourne une copie du format.
        """
        return Format(
            orientation=self.orientation,
            show_indicators_pts=self.show_indicators_pts
        )
