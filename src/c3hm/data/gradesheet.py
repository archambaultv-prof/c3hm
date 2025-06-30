from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.evaluation.indicator import Indicator


class GradeSheet(BaseModel):
    """
    Représente une feuille de notes dans le carnet de notes.
    """
    omnivox_code: str = Field(..., min_length=1)
    comments: dict[str, str]
    grades: dict[str, float]

    @model_validator(mode="after")
    def validate_gradesheet(self) -> Self:
        for v in self.grades.values():
            if v < 0:
                raise ValueError("Les notes ne peuvent pas être négatives.")
        self.comments = dict((k, v.strip()) for k, v in self.comments.items())

        return self

    def has_grade(self, x: Evaluation | Criterion | Indicator) -> bool:
        """
        Indique si l'évaluation, le critère ou l'indicateur donné a une note.
        """
        id = x.id
        return id in self.grades

    def get_grade(self,
                  x: Evaluation | Criterion | Indicator,
                  precision: int = 1,
                  can_exceed_pts: bool = False
                  ) -> Decimal:
        """
        Retourne la note pour l'évaluation, le critère ou l'indicateur donné.
        """
        id = x.id
        grade = self.grades[id]
        grade = Decimal(str(round(grade, precision))).quantize(Decimal("0.1") ** precision)
        if grade > x.points and not can_exceed_pts:
            raise ValueError(
                f"La note {grade} pour {x.name} dépasse le maximum de points {x.points}."
            )
        return grade

    def get_percentage(self,
                       x: Evaluation | Criterion | Indicator,
                       quantize: Decimal = Decimal("0.0001")
                      ) -> Decimal:
        """
        Retourne le pourcentage de la note pour l'évaluation, le critère ou l'indicateur donné.
        Le pourcentage est exprimé en tant que fraction (0.0 à 1.0) de la note maximale.
        """
        grade = self.get_grade(x, precision=2)
        return max(Decimal(0), min(Decimal(1), (grade / x.points).quantize(quantize)))

    def has_comment(self, x: Evaluation | Criterion | Indicator) -> bool:
        """
        Indique si l'évaluation, le critère ou l'indicateur donné a un commentaire.
        """
        id = x.id
        return id in self.comments

    def get_comment(self, x: Evaluation | Criterion | Indicator) -> str:
        """
        Retourne le commentaire pour l'évaluation, le critère ou l'indicateur donné.
        """
        id = x.id
        return self.comments[id]

    def has_criteria_comments(self, eval: Evaluation) -> bool:
        """
        Indique si l'évaluation a des commentaires pour ses critères.
        """
        ls = []
        for c in eval.criteria:
            ls.append(c)
            ls.extend(c.indicators)
        return any(self.has_comment(c) for c in ls)
