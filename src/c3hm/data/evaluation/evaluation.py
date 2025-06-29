from decimal import Decimal
from typing import ClassVar, Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.student.student import Student
from c3hm.utils.decimal import decimal_to_number, is_multiple_of_quantum, round_to_nearest_quantum


class Evaluation(BaseModel):
    """
    Information sur une évaluation.
    """
    name: str = Field(..., min_length=1)
    grade_step: Decimal = Field(
        Decimal("1"),
        ge=Decimal("0"),
        description="Pas de note pour l'évaluation, en points."
    )
    criteria: list[Criterion] = Field(..., min_length=1)
    override_grade: Decimal | None = Field(..., ge=Decimal(0))
    evaluated_student: Student | None
    comment: str

    grade_step_default: ClassVar[Decimal] = Decimal("1")

    def title(self) -> str:
        """
        Retourne le titre de la grille d'évaluation.
        """
        endash = "\u2013"
        title = "Grille d'évaluation"
        title += f" {endash} {self.name}"
        return title

    @property
    def has_grade(self) -> bool:
        """
        Indique si le critère est noté.
        """
        return self.override_grade is not None or self.criteria[0].has_grade

    @property
    def has_criteria_comments(self) -> bool:
        """
        Indique si au moins un critère a un commentaire.
        """
        return any(criterion.has_comments for criterion in self.criteria)

    def get_grade(self) -> Decimal:
        """
        Retourne la note de l'évaluation, en tenant compte de l'override si présent.
        """
        if not self.has_grade:
            raise ValueError(
                "L'évaluation n'est pas notée."
            )
        if self.override_grade is None:
            return sum((criterion.get_grade() for criterion in self.criteria), # type: ignore
                       start=Decimal(0))
        else:
            return self.override_grade

    @model_validator(mode="after")
    def validate_evaluation(self) -> Self:
        """
        Valide que les critères de l'évaluation sont correctement définis.
        """
        # Pas de notation en lien avec les critères
        for criterion in self.criteria:
            for indicator in criterion.indicators:
                if not is_multiple_of_quantum(indicator.points, self.grade_step):
                    raise ValueError(
                        f"La valeur des points ({indicator.points}) de l'indicateur "
                        f"'{indicator.name}' du critère '{criterion.name}' n'est pas un "
                        f"multiple du pas de notation ({self.grade_step})."
                    )

        # Vérifie que les points des critères sont des multiples du pas de notation
        if self.override_grade:
            # Tous les critères doivent être notés
            if not all(criterion.has_grade for criterion in self.criteria):
                raise ValueError(
                    "Tous les critères de l'évaluation doivent être notés si une note manuelle "
                    "est définie."
                )

            if self.override_grade > self.points:
                raise ValueError(
                    f"La valeur de la note manuelle ({self.override_grade}) ne peut pas dépasser "
                    f"le nombre total de points attribués à l'évaluation ({self.points})."
                )
            if not is_multiple_of_quantum(self.override_grade, self.grade_step):
                self.override_grade = round_to_nearest_quantum(self.override_grade,
                                                               self.grade_step)
        else:
            # Soit tous les critères sont notés, soit aucun
            if (any(criterion.has_grade for criterion in self.criteria) and
                not all(criterion.has_grade for criterion in self.criteria)):
                raise ValueError(
                    "Tous les critères de l'évaluation doivent être notés ou aucun ne doit l'être "
                )
        if self.has_grade and self.evaluated_student is None:
            raise ValueError(
                "Une évaluation notée doit être associée à un étudiant évalué."
            )
        if not self.has_grade and self.evaluated_student is not None:
            raise ValueError(
                "Une évaluation non notée ne doit pas être associée à un étudiant évalué."
            )
        for criterion in self.criteria:
            if (criterion.override_grade and
                not is_multiple_of_quantum(criterion.override_grade, self.grade_step)):
                criterion.override_grade = round_to_nearest_quantum(
                    criterion.override_grade, self.grade_step
                )
            for indicator in criterion.indicators:
                if (indicator.grade and
                    not is_multiple_of_quantum(indicator.grade, self.grade_step)):
                    indicator.grade = round_to_nearest_quantum(
                        indicator.grade, self.grade_step
                    )

        # Has

        # Id unique pour les critères
        ids = {}
        for criterion in self.criteria:
            ids[criterion.id] = ids.get(criterion.id, 0) + 1
        if len(ids) != len(self.criteria):
            dups = [id_ for id_, count in ids.items() if count > 1]
            raise ValueError(
                f"Les identifiants des indicateurs du critère '{self.name}' doivent être uniques. "
                f"Les identifiants suivants sont dupliqués : {', '.join(dups)}."
            )

        # Pas d'espace en début et fin de commentaire
        self.comment = self.comment.strip()

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
        if self.override_grade is not None:
            grade = (decimal_to_number(self.override_grade)
                     if convert_decimal else self.override_grade)
        else:
            grade = None
        return {
            "nom": self.name,
            "pas de notation": (self.grade_step
                            if not convert_decimal
                            else decimal_to_number(self.grade_step)),
            "critères": [criterion.to_dict(convert_decimal=convert_decimal)
                         for criterion in self.criteria],
            "note manuelle": grade,
            "étudiant évalué": (self.evaluated_student.to_dict()
                                if self.evaluated_student else None),
            "commentaire": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Evaluation":
        """
        Crée une instance de Evaluation à partir d'un dictionnaire.
        """
        if "étudiant évalué" in data and data["étudiant évalué"] is not None:
            evaluated_student = Student.from_dict(data["étudiant évalué"])
        else:
            evaluated_student = None
        return cls(
            name=data["nom"],
            grade_step=data.get("pas de notation", Decimal("1")),
            criteria=[Criterion.from_dict(criterion) for criterion in data["critères"]],
            override_grade=data.get("note manuelle"),
            evaluated_student=evaluated_student,
            comment=data.get("commentaire", ""),
        )

    def copy(self) -> "Evaluation": # type: ignore
        """
        Retourne une copie de l'évaluation.
        """
        return Evaluation(
            name=self.name,
            grade_step=self.grade_step,
            criteria=[criterion.copy() for criterion in self.criteria],
            override_grade=self.override_grade,
            evaluated_student=self.evaluated_student.copy() if self.evaluated_student else None,
            comment=self.comment
        )
