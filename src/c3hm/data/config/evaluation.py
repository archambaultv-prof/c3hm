from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.config.criterion import Criterion
from c3hm.data.config.grade_level import GradeLevel


class Evaluation(BaseModel):
    """
    Information sur une évaluation.
    """
    model_config = ConfigDict(extra="forbid")

    excel_id: str = "eval"
    name: str = Field(..., min_length=1)
    points_inference_step: Decimal = Decimal("1")
    points_total: Decimal = Field(..., gt=Decimal("0"))
    points_total_nb_of_decimal: int = 0
    grade_levels: list[GradeLevel] = Field(..., min_length=1)
    criteria: list[Criterion] = Field(..., min_length=1)

    def title(self) -> str:
        """
        Retourne le titre de la grille d'évaluation.
        """
        endash = "\u2013"
        title = "Grille d'évaluation"
        title += f" {endash} {self.name}"
        return title


    def get_level_by_percentage(self, percentage: Decimal) -> GradeLevel:
        """
        Retourne le niveau de note correspondant à une note donnée.
        """
        idx = self.get_index_by_percentage(percentage)
        return self.grade_levels[idx]

    def get_index_by_percentage(self, percentage: Decimal) -> int:
        """
        Retourne le niveau de note correspondant à une note donnée.
        """
        if not (0 <= percentage <= 1):
            raise ValueError("Le pourcentage doit être compris entre 0 et 1.")
        for i, level in enumerate(self.grade_levels):
            if percentage * 100 >= level.minimum:
                return i
        raise ValueError("Aucun niveau de note ne correspond au pourcentage donné.")

    @property
    def points(self) -> Decimal:
        """
        Retourne le total des points de l'évaluation.
        Pour compatibilité avec Criterion et Indicator.
        """
        return self.points_total
