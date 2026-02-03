from datetime import date
from typing import Any

from c3hm.data.student import Student


class Indicator:
    def __init__(self, label: str, points: float, descriptors: list[str],
                 graded_level: str | None = None):
        self.label = label
        self.points = points
        self.descriptors = descriptors
        self.graded_level = graded_level

    def copy(self) -> 'Indicator':
        return Indicator(
            label=self.label,
            points=self.points,
            descriptors=self.descriptors.copy(),
            graded_level=self.graded_level
        )

    def validate(self) -> None:
        _assert_non_empty_string(self.label, field_name="indicateur")
        if self.graded_level is not None:
            _assert_non_empty_string(self.graded_level, field_name="niveau noté")
        if not isinstance(self.points, int | float) or self.points < 0:
            raise ValueError(f"Le champ 'points' de l'indicateur '{self.label}' doit être un nombre positif.")
        if len(self.descriptors) != 5:
            raise ValueError(f"L'indicateur '{self.label}' doit contenir une liste de 5 descripteurs.")
        for desc in self.descriptors:
            _assert_non_empty_string(desc, field_name="descripteur")

    def to_dict(self, include_graded_level: bool = False) -> dict:
        d = {
            "indicateur": self.label,
            "points": self.points,
            "descripteurs": self.descriptors
        }
        if include_graded_level:
            d["niveau noté"] = self.graded_level if self.graded_level is not None else ""
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Indicator':
        label = data["indicateur"]
        points = data["points"]
        descriptors = data["descripteurs"]
        graded_level = data.get("niveau noté")
        if graded_level == "":
            graded_level = None
        return cls(label=label, points=points, descriptors=descriptors, graded_level=graded_level)

    @staticmethod
    def level_to_percentage(level: str) -> float:
        if isinstance(level, str):
            level = level.strip().lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ç", "c")
            if level in ("av", "avance"):
                return 1.0
            elif level in ("ac", "acquis"):
                return 0.75
            elif level in ("p", "presque", "ca y est presque"):
                return 0.5
            elif level in ("ap", "en apprentissage", "apprentissage"):
                return 0.25
            elif level in ("n", "non demontre"):
                return  0.0
            else:
                raise ValueError(f"Niveau de performance inconnu: '{level}'")
        else:
            raise TypeError(f"Type de note inattendu: {type(level)}")

    def grade(self) -> float:
        if self.graded_level is None:
            raise ValueError(f"Aucun niveau noté pour l'indicateur '{self.label}'.")
        return self.points * self.level_to_percentage(self.graded_level)

class Criterion:
    def __init__(self, label: str, indicators: list[Indicator], grade_override: float | None = None):
        self.label = label
        self.indicators = indicators
        self.grade_override = grade_override

    def grade(self) -> float:
        if self.grade_override is not None:
            return self.grade_override
        return sum(indicator.grade() for indicator in self.indicators)

    def copy(self) -> 'Criterion':
        return Criterion(
            label=self.label,
            indicators=[indicator.copy() for indicator in self.indicators],
            grade_override=self.grade_override,
        )

    def points(self) -> float:
        return sum(indicator.points for indicator in self.indicators)

    def to_dict(self, include_graded_level: bool = False) -> dict:
        d: dict[str, Any] = {
            "critère": self.label,
        }
        if include_graded_level:
            d["note"] = self.grade_override
        d["indicateurs"] = [indicator.to_dict(include_graded_level) for indicator in self.indicators]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Criterion':
        label = data["critère"]
        indicators = [Indicator.from_dict(ind_data) for ind_data in data["indicateurs"]]
        grade_override = data.get("note")
        return cls(label=label, indicators=indicators, grade_override=grade_override)

    def validate(self) -> None:
        _assert_non_empty_string(self.label, field_name="critère")
        if not self.indicators or not isinstance(self.indicators, list):
            raise ValueError(f"Le critère '{self.label}' doit contenir une liste d'indicateurs non vide.")
        for indicator in self.indicators:
            indicator.validate()
        if self.grade_override is not None:
            if not isinstance(self.grade_override, int | float):
                raise ValueError(f"La note du critère '{self.label}' doit être un nombre.")
            if self.grade_override < 0 or self.grade_override > self.points():
                raise ValueError(
                    f"La note du critère '{self.label}' doit être entre 0 et {self.points()} points."
                )

class Grid:
    def __init__(self, criteria: list[Criterion]):
        self.criteria = criteria

    def grade(self) -> float:
        return sum(round(criterion.grade(), 0) for criterion in self.criteria)

    def copy(self) -> 'Grid':
        return Grid(criteria=[criterion.copy() for criterion in self.criteria])

    def to_dict(self, include_graded_level: bool = False) -> list[dict]:
        return [criterion.to_dict(include_graded_level) for criterion in self.criteria]

    @classmethod
    def from_dict(cls, data: list[dict]) -> 'Grid':
        criteria = [Criterion.from_dict(crit_data) for crit_data in data]
        return cls(criteria=criteria)

    def validate(self) -> None:
        sum_points = 0.0
        if not self.criteria or not isinstance(self.criteria, list):
            raise ValueError("La grille doit contenir une liste de critères non vide.")
        for criterion in self.criteria:
            criterion.validate()
            sum_points += criterion.points()
        if sum_points != 100.0:
            raise ValueError(f"La somme totale des points des critères doit être égale à 100. Total trouvé: {sum_points}")

class Rubric:
    def __init__(self, course: str, session: str, evaluation: str, grid: Grid,
                 show_criteria_points: bool = True, show_levels_percentage: bool = True,
                 student: Student | None = None, grade: float | None = None, comment: str | None = None):
        self.course = course
        self.session = session
        self.evaluation = evaluation
        self.grid = grid
        self.show_criteria_points = show_criteria_points
        self.show_levels_percentage = show_levels_percentage
        self.student = student
        self.grade = grade
        self.comment = comment

    def final_grade(self) -> float:
        if self.grade is not None:
            return self.grade
        return self.grid.grade()

    def grid_grade(self) -> float:
        return self.grid.grade()

    def copy(self) -> 'Rubric':
        return Rubric(
            course=self.course,
            session=self.session,
            evaluation=self.evaluation,
            grid=self.grid.copy(),
            show_criteria_points=self.show_criteria_points,
            show_levels_percentage=self.show_levels_percentage,
            student=self.student.copy() if self.student else None,
            grade=self.grade,
            comment=self.comment
        )

    def to_dict(self) -> dict:
        d = {}
        if self.student:
            d["étudiant"] = {
                "prénom": self.student.firstname,
                "nom": self.student.surname,
                "matricule": self.student.omnivox_id
            }
            d["note"] = self.grade
            d["commentaire"] = self.comment if self.comment is not None else ""
        d.update({
            "cours": self.course,
            "session": self.session,
            "évaluation": self.evaluation,
            "afficher les points des critères": self.show_criteria_points,
            "afficher les pourcentages des niveaux": self.show_levels_percentage,
            "grille": self.grid.to_dict(include_graded_level=self.student is not None),
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Rubric':
        course = data["cours"]
        session = data["session"]
        evaluation = data["évaluation"]
        show_criteria_points = data["afficher les points des critères"]
        show_levels_percentage = data["afficher les pourcentages des niveaux"]
        grid = Grid.from_dict(data["grille"])
        if "étudiant" in data:
            student_data = data["étudiant"]
            firstname = student_data["prénom"]
            surname = student_data["nom"]
            student = Student(
                firstname=firstname,
                surname=surname,
                omnivox_id=student_data.get("matricule", "")
            )
        else:
            student = None
        grade = data.get("note")
        comment = data.get("commentaire")
        if comment == "":
            comment = None
        return cls(course=course, session=session, evaluation=evaluation, grid=grid,
                   show_criteria_points=show_criteria_points, show_levels_percentage=show_levels_percentage,
                   student=student, grade=grade, comment=comment)

    def validate(self) -> None:
        _assert_non_empty_string(self.course, field_name="cours")
        _assert_non_empty_string(self.session, field_name="session")
        _assert_non_empty_string(self.evaluation, field_name="évaluation")
        self.grid.validate()
        if self.student:
            self.student.validate()
        if self.grade is not None and (not isinstance(self.grade, int | float) or self.grade < 0 or self.grade > 100):
            raise ValueError("La note doit être un nombre entre 0 et 100.")

    @classmethod
    def template(cls) -> 'Rubric':
        """
        Retourne une grille d'évaluation modèle. Cette grille n'est pas valide
        au sens de la validation car elle n'a pas de nom de cours et
        d'évaluation.
        """
        descriptors = [
                        "Descripteur 1",
                        "Descripteur 2",
                        "Descripteur 3",
                        "Descripteur 4",
                        "Descripteur 5",
                    ]
        criteria = [
            Criterion(
                label="Critère 1",
                indicators=[
                    Indicator(
                        label="Indicateur 1",
                        points=20,
                        descriptors=descriptors
                    ),
                    Indicator(
                        label="Indicateur 2",
                        points=20,
                        descriptors=descriptors
                    ),
                ]
            ),
            Criterion(
                label="Critère 2",
                indicators=[
                    Indicator(
                        label="Indicateur 3",
                        points=20,
                        descriptors=descriptors
                    ),
                    Indicator(
                        label="Indicateur 4",
                        points=20,
                        descriptors=descriptors
                    ),
                    Indicator(
                        label="Indicateur 5",
                        points=20,
                        descriptors=descriptors
                    ),
                ]
            ),
        ]
        g = Grid(criteria=criteria)
        r = cls(
            course="",
            session=_get_current_semester(),
            evaluation="",
            grid=g,
            show_criteria_points=True,
            show_levels_percentage=True,
        )
        return r

def _get_current_semester() -> str:
    """
    Retourne le semestre actuel
    """
    today = date.today()
    year = today.year
    if today.month <= 5:
        return f"Hiver {year}"
    elif today.month <= 7:
        return f"Été {year}"
    else:
        return f"Automne {year}"

def _assert_non_empty_string(value: Any, field_name: str) -> None:
    if value is None or not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"Le champ '{field_name}' doit être une chaîne de caractères non vide.")
