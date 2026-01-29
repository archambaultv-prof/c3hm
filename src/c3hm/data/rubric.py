from datetime import date
from typing import Any

from c3hm.data.student import Student, find_student_by_name


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

class Criterion:
    def __init__(self, label: str, indicators: list[Indicator]):
        self.label = label
        self.indicators = indicators

    def copy(self) -> 'Criterion':
        return Criterion(
            label=self.label,
            indicators=[indicator.copy() for indicator in self.indicators]
        )

    def points(self) -> float:
        return sum(indicator.points for indicator in self.indicators)

    def to_dict(self, include_graded_level: bool = False) -> dict:
        return {
            "critère": self.label,
            "indicateurs": [indicator.to_dict(include_graded_level) for indicator in self.indicators],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Criterion':
        label = data["critère"]
        indicators = [Indicator.from_dict(ind_data) for ind_data in data["indicateurs"]]
        return cls(label=label, indicators=indicators)

    def validate(self) -> None:
        _assert_non_empty_string(self.label, field_name="critère")
        if not self.indicators or not isinstance(self.indicators, list):
            raise ValueError(f"Le critère '{self.label}' doit contenir une liste d'indicateurs non vide.")
        for indicator in self.indicators:
            indicator.validate()

class Grid:
    def __init__(self, criteria: list[Criterion]):
        self.criteria = criteria

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
                "nom": self.student.name,
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
            student = Student(
                name=student_data.get("nom", ""),
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

def validate_student(rubric: dict, student_list: list[Student] | None) -> None:
    if "étudiant" not in rubric:
        raise ValueError("La grille de l'étudiant doit contenir une section 'étudiant'.")
    student = rubric["étudiant"]
    if "nom" not in student or not isinstance(student["nom"], str) or student["nom"].strip() == "":
        raise ValueError("Le champ 'nom' de l'étudiant doit être une chaîne de caractères non vide.")
    if "matricule" not in student:
        if not student_list:
            raise ValueError("Le fichier d'étudiants doit être fourni pour faire la correspondance par nom.")
        s1 = find_student_by_name(student["nom"], student_list)
        rubric["étudiant"]["matricule"] = s1.omnivox_id
        rubric["étudiant"]["nom"] = s1.full_name()

def validate_rubric(rubric: dict) -> None:
    """Validate that the rubric has the required structure."""

    assert_total_points(rubric)
    validate_descriptors(rubric)

    if is_single_student_rubric(rubric):
        _assert_non_empty_string(rubric["étudiant"], "nom")
        _assert_non_empty_string(rubric["étudiant"], "matricule")
        none_if_missing_or_empty(rubric, "commentaire")
        for item in rubric.get("critères", []):
            none_if_missing_or_empty(item, "commentaire")

def none_if_missing_or_empty(d: dict, field_name: str) -> None:
    if field_name not in d:
        d[field_name] = None
        return
    value = d[field_name]
    if isinstance(value, str):
        if value.strip() == "":
            d[field_name] = None
    elif value is None:
        return
    else:
        raise ValueError(f"Le champ '{field_name}' doit être une chaîne de caractères.")

def _assert_non_empty_string(value: Any, field_name: str) -> None:
    if value is None or not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"Le champ '{field_name}' doit être une chaîne de caractères non vide.")

def assert_total_points(rubric: dict) -> None:
    total_points = 0.0
    for node in rubric.get("critères", []):
        if "critère" in node:
            if "points" not in node:
                raise ValueError(f"Le critère '{node['critère']}' doit contenir un champ 'points'.")
            points = node["points"]
            if not isinstance(points, int | float) or points < 0:
                raise ValueError(f"Le champ 'points' doit être un nombre positif. Valeur trouvée: {points}")
            total_points += points
    if round(total_points, 2) != 100:
        raise ValueError(f"La somme totale des points des critères doit être égale à 100. Total trouvé: {total_points}")

def validate_descriptors(rubric: dict) -> None:
    for node in rubric.get("critères", []):
        if "critère" in node and "descripteurs" in node:
            descripteurs = node["descripteurs"]
            if not isinstance(descripteurs, list) or len(descripteurs) != 5:
                raise ValueError(f"Le critère '{node['critère']}' doit contenir une liste de 5 descripteurs.")
            for desc in descripteurs:
                if not isinstance(desc, str) or desc.strip() == "":
                    raise ValueError(f"Chaque descripteur du critère '{node['critère']}' doit être une chaîne de caractères non vide.")

def process_single_student_rubric(rubric: dict) -> dict:
    """
    Calcule différentes valeurs pour un étudiant à partir de la grille de correction.
    """
    grade = 0.0
    for node in rubric["critères"]:
        if "section" in node:
            continue
        if "pourcentage" not in node:
            raise ValueError("Chaque critère doit contenir un pourcentage.")
        node["pourcentage"] = parse_percent(node["pourcentage"])
        node["note"] = round(node["pourcentage"] * node["points"], 1)
        grade += node["note"]
    bonus_malus = rubric.get("bonus malus", {})
    if bonus_malus.get("points") is not None:
        grade += bonus_malus["points"]
    rubric["note"] = round(grade, 0)
    if "commentaire" in rubric and rubric["commentaire"] is not None and rubric["commentaire"].strip():
        rubric["commentaire"] = rubric["commentaire"].strip()
    elif rubric["note"] >= 90:
        rubric["commentaire"] = "Très bon travail!"
    else:
        rubric["commentaire"] = None
    return rubric


def parse_percent(note: str | float | int | None) -> float:
    if note is None:
        raise ValueError("La note ne peut pas être None")
    if isinstance(note, float | int):
        grade = float(note)
    elif isinstance(note, str):
        note = note.strip().lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("ç", "c")
        if note in ("av", "avance"):
            grade =  1.0
        elif note in ("ac", "acquis"):
            grade =  0.75
        elif note in ("p", "presque", "ca y est presque"):
            grade =  0.5
        elif note in ("ap", "en apprentissage", "apprentissage"):
            grade =  0.25
        elif note in ("i", "insuffisant", "donnees insuffisantes"):
            grade =  0.0
        else:
            grade =  float(note)
    else:
        raise TypeError(f"Type de note inattendu: {type(note)}")
    if not (0.0 <= grade <= 1.0):
        raise ValueError(f"La note doit être entre 0 et 1. Valeur reçue: {note}")
    return grade
