from decimal import Decimal

from pydantic import Field

from c3hm.data.rubric import Criterion, Indicator, Rubric


class GradedIndicator(Indicator):
    """
    Représente un indicateur d'évaluation corrigé.
    """
    grade: Decimal
    comment: str = Field(
        default="",
        description="Commentaire de l'évaluateur sur l'indicateur",
    )

class GradedCriterion(Criterion):
    """
    Représente un critère d'évaluation corrigé.
    """
    indicators: list[GradedIndicator]
    grade: Decimal
    comment: str = Field(
        default="",
        description="Commentaire de l'évaluateur sur le critère",
    )

class GradedRubric(Rubric):
    """
    Représente une grille d'évaluation corrigée.
    """
    criteria: list[GradedCriterion] = Field(..., min_length=1)
