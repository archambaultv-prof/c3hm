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
    show_indicators_percent: bool = Field(
        default=True,
        description="Indique si le poids des indicateurs doit être affiché."
    )

    columns_width: list[float | None] = Field(
        default_factory=list,
        description="Largeur des colonnes de la grille d'évaluation. "
    )

    columns_width_comments: list[float | None] = Field(
        default_factory=list,
        description="Largeur des colonnes de commentaires de la grille d'évaluation. "
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le format de la grille d'évaluation.
        """
        return {
            "orientation": self.orientation,
            "afficher le pourcentage des indicateurs": self.show_indicators_percent,
            "largeur des colonnes": self.columns_width,
            "largeur des colonnes avec commentaires": self.columns_width_comments,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Format":
        """
        Crée une instance de Format à partir d'un dictionnaire.
        """
        return cls(
            orientation=data.get("orientation"),
            show_indicators_percent=data.get("afficher le pourcentage des indicateurs", True),
            columns_width=data.get("largeur des colonnes", []),
            columns_width_comments=data.get("largeur des colonnes avec commentaires", []),
        )

    def copy(self) -> "Format": # type: ignore
        """
        Retourne une copie du format.
        """
        return Format(
            orientation=self.orientation,
            show_indicators_percent=self.show_indicators_percent,
            columns_width=self.columns_width.copy(),
            columns_width_comments=self.columns_width_comments.copy(),
        )
