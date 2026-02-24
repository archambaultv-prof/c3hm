from datetime import date

from c3hm.data.criterion import Criterion
from c3hm.data.grid import Grid
from c3hm.data.indicator import Indicator
from c3hm.data.level import DEFAULT_LEVELS
from c3hm.data.student import Student
from c3hm.data.utils import assert_non_empty_string


class Rubric:
    def __init__(
        self,
        course: str,
        session: str,
        evaluation: str,
        grid: Grid,
        student: Student | None = None,
        teammates: list[Student] | None = None,
        grade_override: float | None = None,
        comment: str | None = None,
    ):
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

    def copy(self) -> "Rubric":
        teammates = [tm.copy() for tm in self.teammates] if self.teammates else None
        return Rubric(
            course=self.course,
            session=self.session,
            evaluation=self.evaluation,
            grid=self.grid.copy(),
            student=self.student.copy() if self.student else None,
            teammates=teammates if teammates is not None else None,
            grade_override=self.grade_override,
            comment=self.comment,
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
        d.update(
            {
                "cours": self.course,
                "session": self.session,
                "évaluation": self.evaluation,
                "grille": self.grid.to_dict(include_graded_level=self.student is not None),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
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
        return cls(
            course=course,
            session=session,
            evaluation=evaluation,
            grid=grid,
            student=student,
            teammates=teammates,
            grade_override=grade,
            comment=comment,
        )

    def validate(self) -> None:
        assert_non_empty_string(self.course, field_name="cours")
        assert_non_empty_string(self.session, field_name="session")
        assert_non_empty_string(self.evaluation, field_name="évaluation")
        self.grid.validate()
        if self.student:
            self.student.validate()
        if self.grade_override is not None and (
            not isinstance(self.grade_override, int | float) or self.grade_override < 0 or self.grade_override > 100
        ):
            raise ValueError("La note doit être un nombre entre 0 et 100.")

    @classmethod
    def template(cls) -> "Rubric":
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
                    Indicator(label="Indicateur 1", points=20, descriptors=descriptors),
                    Indicator(label="Indicateur 2", points=20, descriptors=descriptors),
                ],
            ),
            Criterion(
                label="Critère 2",
                indicators=[
                    Indicator(label="Indicateur 3", points=20, descriptors=descriptors),
                    Indicator(label="Indicateur 4", points=20, descriptors=descriptors),
                    Indicator(label="Indicateur 5", points=20, descriptors=descriptors),
                ],
            ),
        ]
        g = Grid(criteria=criteria, levels=DEFAULT_LEVELS, show_criteria_points=True, show_levels_percentage=True)
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


def validate_rubrics(rubrics: list[Rubric]) -> None:
    """
    Valide une liste de grilles de correction. Cette validation inclut la validation
    de chaque grille individuellement, ainsi que la validation des coéquipiers.
    """
    for rubric in rubrics:
        rubric.validate()
    validate_teammates(rubrics)


def validate_teammates(rubrics: list[Rubric]) -> None:
    """
    Valide que les coéquipiers d'une liste de grilles forment des cliques
    (équipes complètes). Une équipe est une clique si tous les membres ont les
    mêmes coéquipiers (pas de membre qui aurait un coéquipier en dehors du
    groupe)
    """
    student_to_teammates: dict[str, set[str]] = {}
    for rubric in rubrics:
        if rubric.student is None:
            raise ValueError("Toutes les grilles doivent être associées à un étudiant pour valider les coéquipiers.")
        student_id = rubric.student.omnivox_id
        teammates_ids = set(tm.omnivox_id for tm in rubric.teammates)
        student_to_teammates[student_id] = teammates_ids

    # Vérifier les relations bidirectionnelles et construire les groupes
    visited = set()
    for student_id in student_to_teammates:
        if student_id in visited:
            continue

        # Trouver tous les étudiants du groupe selon cet étudiant
        group = set(student_to_teammates[student_id])
        group.add(student_id)
        visited.update(group)

        # Vérifier que tous les étudiants du groupe ont exactement les mêmes coéquipiers (le groupe moins eux-mêmes)
        for member_id in group:
            expected_teammates = group - {member_id}
            actual_teammates = student_to_teammates.get(member_id, set())
            if expected_teammates != actual_teammates:
                raise ValueError(
                    f"Incohérence dans les coéquipiers pour l'étudiant {member_id}. "
                    f"Coéquipiers attendus: {expected_teammates}, coéquipiers trouvés: {actual_teammates}"
                )
