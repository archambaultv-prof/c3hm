import unicodedata
from datetime import date
from typing import Any

from c3hm.data.student import Student


class Level:
    def __init__(self, label: str, percentage: float, short_label: list[str] | None = None):
        self.label = label
        self.percentage = percentage
        self.short_label = short_label

    def match_label(self, label: str) -> bool:
        label = self._to_matchable(label)
        if label == self._to_matchable(self.label):
            return True
        elif self.short_label is not None:
            return any(label == self._to_matchable(short) for short in self.short_label)
        return False

    def _to_matchable(self, text: str) -> str:
        return self._remove_accents(unicodedata.normalize("NFD", text)).casefold().strip()

    def _remove_accents(self, text: str) -> str:
        return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    def copy(self) -> 'Level':
        return Level(label=self.label, percentage=self.percentage, short_label=self.short_label.copy() if self.short_label else None)

    def validate(self) -> None:
        _assert_non_empty_string(self.label, field_name="niveau")
        if not isinstance(self.percentage, int | float) or self.percentage < 0 or self.percentage > 1:
            raise ValueError(f"Le champ 'pourcentage' du niveau '{self.label}' doit être un nombre entre 0 et 1.")
        if self.short_label is not None and (not isinstance(self.short_label, list) or not all(isinstance(s, str) and s.strip() != "" for s in self.short_label)):
            raise ValueError(f"Le champ 'abréviations' du niveau '{self.label}' doit être une liste de chaînes de caractères non vides.")

    def to_dict(self) -> dict:
        d = {
            "niveau": self.label,
            "pourcentage": self.percentage,
        }
        if self.short_label is not None:
            d["abréviations"] = self.short_label
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Level':
        label = data["niveau"]
        percentage = data["pourcentage"]
        short_label = data.get("abréviations")
        return cls(label=label, percentage=percentage, short_label=short_label)

DEFAULT_LEVELS = [
    Level(label="Bien maîtrisé", percentage=1.0, short_label=["m", "maîtrisé"]),
    Level(label="Acquis", percentage=0.75, short_label=["ac"]),
    Level(label="Ça y est presque!", percentage=0.5, short_label=["p", "presque"]),
    Level(label="En apprentissage", percentage=0.25, short_label=["ap", "apprentissage"]),
    Level(label="Non démontré", percentage=0.0, short_label=["n", "nd"]),
]

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

    def grade(self, grid: 'Grid') -> float:
        if self.graded_level is None:
            raise ValueError(f"Aucun niveau noté pour l'indicateur '{self.label}'.")
        return self.points * grid.level_to_percentage(self.graded_level)

class Criterion:
    def __init__(self, label: str, indicators: list[Indicator], grade_override: float | None = None):
        self.label = label
        self.indicators = indicators
        self.grade_override = grade_override

    def grade(self, grid: 'Grid') -> float:
        if self.grade_override is not None:
            return self.grade_override
        return sum(indicator.grade(grid) for indicator in self.indicators)

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
            d["note ajustée"] = self.grade_override
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
    def __init__(self, criteria: list[Criterion], levels: list[Level] | None = None,
                 show_criteria_points: bool = True, show_levels_percentage: bool = True,):
        self.criteria = criteria
        self.levels = levels if levels is not None else DEFAULT_LEVELS
        self.show_criteria_points = show_criteria_points
        self.show_levels_percentage = show_levels_percentage

    def grade(self) -> float:
        return sum(round(criterion.grade(self), 0) for criterion in self.criteria)

    def copy(self) -> 'Grid':
        new_levels = [level.copy() for level in self.levels] if self.levels is not None else None
        return Grid(criteria=[criterion.copy() for criterion in self.criteria], levels=new_levels,
                    show_criteria_points=self.show_criteria_points,
                    show_levels_percentage=self.show_levels_percentage,)

    def to_dict(self, include_graded_level: bool = False) -> dict:
        d = {
            "afficher les points des critères": self.show_criteria_points,
            "afficher les pourcentages des niveaux": self.show_levels_percentage,
            "niveaux": [level.to_dict() for level in self.levels],
            "critères": [criterion.to_dict(include_graded_level) for criterion in self.criteria]
        }
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Grid':
        criteria = [Criterion.from_dict(crit_data) for crit_data in data["critères"]]
        levels = [Level.from_dict(level_data) for level_data in data["niveaux"]]
        show_criteria_points = data.get("afficher les points des critères", True)
        show_levels_percentage = data.get("afficher les pourcentages des niveaux", True)
        return cls(criteria=criteria, levels=levels,
                   show_criteria_points=show_criteria_points,
                   show_levels_percentage=show_levels_percentage)

    def level_to_percentage(self, level: str) -> float:
        if isinstance(level, str):
            for level_item in self.levels:
                if level_item.match_label(level):
                    return level_item.percentage
            else:
                raise ValueError(f"Niveau de performance inconnu: '{level}'")
        else:
            raise TypeError(f"Type de note inattendu: {type(level)}")

    def level_to_rank(self, level: str) -> int:
        if isinstance(level, str):
            for idx, level_item in enumerate(self.levels):
                if level_item.match_label(level):
                    return idx
            else:
                raise ValueError(f"Niveau de performance inconnu: '{level}'")
        else:
            raise TypeError(f"Type de note inattendu: {type(level)}")

    def validate(self) -> None:
        sum_points = 0.0
        if not self.criteria or not isinstance(self.criteria, list):
            raise ValueError("La grille doit contenir une liste de critères non vide.")
        for criterion in self.criteria:
            criterion.validate()
            sum_points += criterion.points()
        if sum_points != 100.0:
            raise ValueError(f"La somme totale des points des critères doit être égale à 100. Total trouvé: {sum_points}")
        if not self.levels or not isinstance(self.levels, list):
            raise ValueError("La grille doit contenir une liste de niveaux non vide.")
        for level in self.levels:
            level.validate()
        nb_levels = len(self.levels)
        for criterion in self.criteria:
            for indicator in criterion.indicators:
                if indicator.descriptors is None or len(indicator.descriptors) != nb_levels:
                    raise ValueError(
                        f"L'indicateur '{indicator.label}' du critère '{criterion.label}' doit contenir une liste de descripteurs de longueur égale au nombre de niveaux ({nb_levels})."
                    )
                if indicator.graded_level is not None and not any(level.match_label(indicator.graded_level) for level in self.levels):
                    raise ValueError(
                        f"Niveau noté inconnu '{indicator.graded_level}' pour l'indicateur '{indicator.label}'."
                    )

    def is_graded(self) -> bool:
        """
        Vérifie si tous les indicateurs de la grille ont été notés.
        """
        for criterion in self.criteria:
            for indicator in criterion.indicators:
                if indicator.graded_level is None or indicator.graded_level.strip() == "":
                    return False
        return True

class Rubric:
    def __init__(self, course: str, session: str, evaluation: str, grid: Grid,
                 student: Student | None = None, teammates: list[Student] | None = None,
                 grade_override: float | None = None, comment: str | None = None):
        self.course = course
        self.session = session
        self.evaluation = evaluation
        self.grid = grid
        self.student = student
        self.teammates = teammates if teammates is not None else []
        self.grade_override = grade_override
        self.comment = comment

    def final_grade(self) -> float:
        if self.grade_override is not None:
            return self.grade_override
        return self.grid.grade()

    def grid_grade(self) -> float:
        return self.grid.grade()

    def copy(self) -> 'Rubric':
        teammates = [tm.copy() for tm in self.teammates] if self.teammates else None
        return Rubric(
            course=self.course,
            session=self.session,
            evaluation=self.evaluation,
            grid=self.grid.copy(),
            student=self.student.copy() if self.student else None,
            teammates=teammates if teammates is not None else None,
            grade_override=self.grade_override,
            comment=self.comment
        )

    def to_dict(self) -> dict:
        d = {}
        if self.student:
            d["étudiant"] = {
                "prénom": self.student.firstname,
                "nom": self.student.surname,
                "matricule": self.student.omnivox_id,
            }
            d["coéquipiers"] = [tm.to_dict() for tm in self.teammates]
            d["note ajustée"] = self.grade_override
            d["commentaire"] = self.comment if self.comment is not None else ""
        d.update({
            "cours": self.course,
            "session": self.session,
            "évaluation": self.evaluation,
            "grille": self.grid.to_dict(include_graded_level=self.student is not None),
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Rubric':
        course = data["cours"]
        session = data["session"]
        evaluation = data["évaluation"]
        grid = Grid.from_dict(data["grille"])
        if "étudiant" in data:
            student = Student.from_dict(data["étudiant"])
            teammates = [Student.from_dict(tm_data) for tm_data in data.get("coéquipiers", [])]
        else:
            student = None
            teammates = None
        grade = data.get("note ajustée")
        comment = data.get("commentaire")
        if comment == "":
            comment = None
        return cls(course=course, session=session, evaluation=evaluation, grid=grid,
                   student=student, teammates=teammates,
                   grade_override=grade, comment=comment)

    def validate(self) -> None:
        _assert_non_empty_string(self.course, field_name="cours")
        _assert_non_empty_string(self.session, field_name="session")
        _assert_non_empty_string(self.evaluation, field_name="évaluation")
        self.grid.validate()
        if self.student:
            self.student.validate()
        if self.grade_override is not None and (not isinstance(self.grade_override, int | float) or self.grade_override < 0 or self.grade_override > 100):
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
        g = Grid(criteria=criteria, levels=DEFAULT_LEVELS,
                 show_criteria_points=True, show_levels_percentage=True)
        r = cls(
            course="",
            session=_get_current_semester(),
            evaluation="",
            grid=g,
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
