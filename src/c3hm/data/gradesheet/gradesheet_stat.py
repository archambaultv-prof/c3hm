from c3hm.data.config.criterion import Criterion
from c3hm.data.config.evaluation import Evaluation
from c3hm.data.config.indicator import Indicator
from c3hm.data.gradesheet.gradesheet import GradeSheet


class GradeSheetStat:
    """
    Représente les statistiques d'une feuille de notes.
    """
    def __init__(self, grade_sheets: list[GradeSheet]) -> None:
        self.grade_sheets = grade_sheets

    def get_grade_average(self, x: Evaluation | Criterion | Indicator) -> float:
        """
        Retourne la moyenne des notes pour l'évaluation, le critère ou l'indicateur donné.
        """
        if not self.grade_sheets:
            return 0.0
        grades = [float(sheet.get_grade(x)) for sheet in self.grade_sheets]
        avg = sum(grades) / len(grades)
        return avg

    def get_percentage_average(self, x: Evaluation | Criterion | Indicator) -> float:
        """
        Retourne la moyenne des pourcentages pour l'évaluation, le critère ou l'indicateur donné.
        """
        if not self.grade_sheets:
            return 0.0
        percentages = [float(sheet.get_percentage(x)) for sheet in self.grade_sheets]
        avg = sum(percentages) / len(percentages)
        return avg
