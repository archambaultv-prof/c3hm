from datetime import date

from c3hm.data import (
    JSON_KEY_COMMENT,
    JSON_KEY_COURSE,
    JSON_KEY_EVALUATION,
    JSON_KEY_GRADE_OVERRIDE,
    JSON_KEY_GRID,
    JSON_KEY_SESSION,
    JSON_KEY_STUDENT,
    JSON_KEY_TEAMMATES,
)
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
        grade_override: float | str | None = None,
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
        if self.grade_override is not None and isinstance(self.grade_override, int | float):
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
            d[JSON_KEY_STUDENT] = self.student.to_dict()
            d[JSON_KEY_TEAMMATES] = [tm.to_dict() for tm in self.teammates]
            d[JSON_KEY_GRADE_OVERRIDE] = self.grade_override
            d[JSON_KEY_COMMENT] = self.comment if self.comment is not None else ""
        d.update(
            {
                JSON_KEY_COURSE: self.course,
                JSON_KEY_SESSION: self.session,
                JSON_KEY_EVALUATION: self.evaluation,
                JSON_KEY_GRID: self.grid.to_dict(include_graded_level=self.student is not None),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
        course = data[JSON_KEY_COURSE]
        session = data[JSON_KEY_SESSION]
        evaluation = data[JSON_KEY_EVALUATION]
        grid = Grid.from_dict(data[JSON_KEY_GRID])
        if JSON_KEY_STUDENT in data:
            student = Student.from_dict(data[JSON_KEY_STUDENT])
            teammates = [Student.from_dict(tm_data) for tm_data in data.get(JSON_KEY_TEAMMATES, [])]
        else:
            student = None
            teammates = None
        grade = data.get(JSON_KEY_GRADE_OVERRIDE)
        comment = data.get(JSON_KEY_COMMENT)
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
        if isinstance(self.grade_override, str):
            self._process_grade_override_as_level()
        self.grid.validate()
        if self.student:
            self.student.validate()
        if isinstance(self.grade_override, int | float):
            if self.grade_override < 0 or self.grade_override > 100:
                raise ValueError("La note doit être un nombre entre 0 et 100.")
        elif isinstance(self.grade_override, str):
            pass # Ce cas a été géré plus haut
        elif self.grade_override is not None:
            raise ValueError(f"La note {self.grade_override} doit être un nombre ou une chaîne de caractères "
                             f"représentant un niveau de performance. Type : {type(self.grade_override)}")

    def _process_grade_override_as_level(self) -> None:
        """
        Si la grade_override est une chaîne de caractères, on le propage à travers la grille.
        """
        if isinstance(self.grade_override, str):
            self.grid._process_grade_override_as_level(self.grade_override)
        else:
            raise TypeError(f"Type de grade_override inattendu: {type(self.grade_override)}")

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


    def is_graded(self) -> bool:
        """
        Vérifie si la grille a été notée (tous les indicateurs ont un niveau de performance assigné).
        """
        if self.grade_override is not None and isinstance(self.grade_override, str):
            return True  # Si la grille a une grade_override en niveau, on considère qu'elle est notée
        return self.grid.is_graded()

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
    student_to_teamname: dict[str, str | None] = {}
    student_to_teamref: dict[str, bool] = {}
    for rubric in rubrics:
        if rubric.student is None:
            raise ValueError("Toutes les grilles doivent être associées à un étudiant pour valider les coéquipiers.")
        student_id = rubric.student.omnivox_id
        teammates_ids = set(tm.omnivox_id for tm in rubric.teammates)
        student_to_teammates[student_id] = teammates_ids
        student_to_teamname[student_id] = rubric.student.team
        student_to_teamref[student_id] = rubric.student.team_reference

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
        team_ref = None
        team_name = student_to_teamname[student_id]
        for member_id in group:
            expected_teammates = group - {member_id}
            actual_teammates = student_to_teammates.get(member_id, set())
            if expected_teammates != actual_teammates:
                raise ValueError(
                    f"Incohérence dans les coéquipiers pour l'étudiant {member_id}. "
                    f"Coéquipiers attendus: {expected_teammates}, coéquipiers trouvés: {actual_teammates}"
                )
            if (student_to_teamname[member_id] is not None
                and student_to_teamname[member_id] != team_name):
                raise ValueError(
                    f"Incohérence dans les noms d'équipe pour l'étudiant {member_id}. "
                    f"Nom d'équipe attendu: {team_name}, "
                    f"nom d'équipe trouvé: {student_to_teamname[member_id]}"
                )
            if student_to_teamref[member_id]:
                if team_ref is None:
                    team_ref = member_id
                else:
                    raise ValueError(
                        f"Il y a deux références d'équipe dans l'équipe {team_name}"
                    )

def fill_grades_from_team_reference(rubrics: list[Rubric]) -> None:
    """
    Remplit les notes des étudiants à partir de la référence d'équipe. Si un étudiant est une référence d'équipe,
    sa note est utilisée pour remplir les notes de tous les autres membres de son équipe si elles sont absentes.

    Ne copie pas les grade_override.

    Assume que les grilles ont déjà été validées et que les coéquipiers forment des cliques valides.
    """
    team_ref_rubric: dict[str, Rubric] = {}
    for rubric in rubrics:
        if rubric.student and rubric.student.team_reference:
            team_ref_rubric[rubric.student.omnivox_id] = rubric

    for rubric in rubrics:
        if rubric.student and rubric.student.team_reference:
            continue
        # Find the team reference for this student if any
        team_ref = None
        for teammate in rubric.teammates:
            if teammate.omnivox_id in team_ref_rubric:
                team_ref = team_ref_rubric[teammate.omnivox_id]
                break
        if team_ref is None:
            continue
        # Fill the grade from the team reference if it's missing
        for criterion, team_ref_criterion in zip(rubric.grid.criteria, team_ref.grid.criteria, strict=True):
            for indicator, team_ref_indicator in zip(criterion.indicators, team_ref_criterion.indicators, strict=True):
                if indicator.graded_level is None and team_ref_indicator.graded_level is not None:
                    indicator.graded_level = team_ref_indicator.graded_level
        if rubric.comment is None and team_ref.comment is not None:
            rubric.comment = team_ref.comment
