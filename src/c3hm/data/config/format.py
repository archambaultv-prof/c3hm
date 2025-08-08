from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Format(BaseModel):
    """
    Représente le format de la grille d'évaluation.
    """
    model_config = ConfigDict(extra="forbid")

    orientation: None | Literal["portrait", "paysage"] = Field(
        default=None,
        description="Orientation de la grille d'évaluation. Peut être 'portrait' ou 'paysage'."
    )
    show_indicators_points: bool = Field(
        default=False,
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

    show_grade_level_descriptions: bool = Field(
        default=True,
        description="Indique si les descriptions des niveaux doivent être affichées."
    )
