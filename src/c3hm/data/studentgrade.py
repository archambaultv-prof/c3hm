from decimal import Decimal

from pydantic import BaseModel

from c3hm.data.student import Student
from c3hm.utils.decimal import round_to_nearest_quantum


class IndicatorGrade(BaseModel):
    """
    Représente la note d'un indicateur spécifique pour une évaluation.
    """
    grade: Decimal
    percentage: Decimal
    comment: str = ""

    def has_comment(self) -> bool:
        """
        Vérifie si un commentaire est associé à la note de l'indicateur.
        """
        return bool(self.comment.strip())

    def rounded_grade(self, quantum: Decimal) -> Decimal:
        return round_to_nearest_quantum(self.grade, quantum)

class CriterionGrade(BaseModel):
    indicators: list[IndicatorGrade]
    manual_grade: Decimal | None = None
    percentage: Decimal
    comment: str = ""

    def has_comment(self) -> bool:
        """
        Vérifie si un commentaire est associé à la note du critère.
        """
        return bool(self.comment.strip()) or any(indicator.has_comment()
                                                 for indicator in self.indicators)

    def rounded_grade(self, quantum: Decimal) -> Decimal:
        """
        Calcule la note totale du critère en fonction des notes des indicateurs.
        Si une note manuelle est fournie, elle est utilisée à la place.
        """
        if self.manual_grade is not None:
            return round_to_nearest_quantum(self.manual_grade, quantum)
        if not self.indicators:
            raise ValueError("Aucun indicateur n'est défini pour ce critère.")
        s = sum((indicator.grade * indicator.percentage for indicator in self.indicators),
                start=Decimal(0))
        s /= sum(indicator.percentage for indicator in self.indicators)
        return round_to_nearest_quantum(s, quantum)

class StudentGrade(BaseModel):
    """
    Représente la note d'un étudiant pour une évaluation spécifique.
    """
    student: Student
    criteria: list[CriterionGrade]
    comment: str = ""

    def rounded_grade(self, quantum: Decimal) -> Decimal:
        """
        Calcule la note totale de l'étudiant en fonction des notes des critères.
        """
        if not self.criteria:
            raise ValueError("Aucun critère n'est défini pour cet étudiant.")
        s = sum((criterion.rounded_grade(quantum) * criterion.percentage
                 for criterion in self.criteria), start=Decimal(0))
        s /= sum(criterion.percentage for criterion in self.criteria)
        return round_to_nearest_quantum(s, quantum)

    def has_comments(self) -> bool:
        """
        Vérifie si un commentaire est associé à la note de l'étudiant.
        """
        return bool(self.comment.strip()) or any(criterion.has_comment()
                                                 for criterion in self.criteria)

    def has_criteria_comments(self) -> bool:
        """
        Vérifie si des commentaires sont associés aux critères de l'étudiant.
        """
        return any(criterion.has_comment() for criterion in self.criteria)
