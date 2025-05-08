from decimal import Decimal

from pydantic import Field

from c3hm.data.rubric import Criterion, Indicator, Rubric
from c3hm.data.student import Student
from c3hm.utils import decimal_to_number


class GradedIndicator(Indicator):
    """
    Représente un indicateur d'évaluation corrigé.
    """
    grade: Decimal
    comment: str = Field(
        default="",
        description="Commentaire de l'évaluateur sur l'indicateur",
    )

    def to_dict(self):
        d = super().to_dict()
        d["note"] = decimal_to_number(self.grade)
        d["commentaire"] = self.comment
        return d

    @classmethod
    def from_indicator(
        cls,
        indicator: Indicator,
        grade: Decimal,
        comment: str
        ) -> "GradedIndicator":
        """
        Crée un GradedIndicator à partir d'un Indicator.
        """
        return cls(
            name=indicator.name,
            descriptors=indicator.descriptors,
            weight=indicator.weight,
            xl_cell_id=indicator.xl_cell_id,
            grade=grade,
            comment=comment
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

    def to_dict(self):
        d = super().to_dict()
        d["indicateurs"] = [indicator.to_dict() for indicator in self.indicators]
        d["note"] = decimal_to_number(self.grade)
        d["commentaire"] = self.comment
        return d

    @classmethod
    def from_criterion(
        cls,
        criterion: Criterion,
        graded_indicators: list[GradedIndicator],
        grade: Decimal,
        comment: str
        ) -> "GradedCriterion":
        """
        Crée un GradedCriterion à partir d'un Criterion.
        """
        return cls(
            name=criterion.name,
            indicators=graded_indicators,
            points=criterion.total,
            xl_cell_id=criterion.xl_cell_id,
            grade=grade,
            comment=comment
        )

    def has_comments(self) -> bool:
        """
        Vérifie si le critère a des commentaires.
        """
        return any(indicator.comment for indicator in self.indicators) or self.comment != ""

class GradedRubric(Rubric):
    """
    Représente une grille d'évaluation corrigée.
    """
    criteria: list[GradedCriterion] = Field(..., min_length=1)
    student: Student

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la grille d'évaluation corrigée.
        """
        d = super().to_dict()
        d["critères"] = [criterion.to_dict() for criterion in self.criteria]
        d["étudiant"] = self.student.to_dict()
        return d

    @classmethod
    def from_rubric(
        cls,
        rubric: Rubric,
        graded_criteria: list[GradedCriterion],
        student: Student
        ) -> "GradedRubric":
        """
        Crée un GradedRubric à partir d'un Rubric.
        """
        return cls(
            criteria=graded_criteria,
            scale=rubric.scale,
            pts_total=rubric.total,
            pts_precision=rubric.pts_precision,
            student=student
        )
