from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.criterion import Criterion
from c3hm.data.format import Format
from c3hm.data.grade_level import GradeLevel
from c3hm.data.indicator import Indicator


class Config(BaseModel):
    """
    Représente la configuration qui est utilisée par générer la grille de
    correction et les rétroactions.
    """
    model_config = ConfigDict(extra="forbid")

    evaluation_name: str = Field(..., min_length=1)
    evaluation_total: float | None = Field(..., gt=0)
    evaluation_total_nb_decimals: int = Field(..., ge=0)
    evaluation_grade: float | None = Field(..., ge=0)
    evaluation_comment: str | None = Field(..., min_length=1)

    student_name: str | None = Field(..., min_length=1)
    student_omnivox: str | None = Field(..., min_length=1)
    student_teammates: list[str]

    grade_levels: list[GradeLevel]

    criteria: list[Criterion]

    format: Format

    def get_total(self) -> float:
        """
        Retourne le total des points de l'évaluation.
        """
        if self.evaluation_total is None:
            raise ValueError("Le total des points de l'évaluation n'est pas défini.")
        return self.evaluation_total

    def evaluation_title(self) -> str:
        """
        Retourne le titre de la grille d'évaluation.
        """
        endash = "\u2013"
        title = "Grille d'évaluation"
        title += f" {endash} {self.evaluation_name}"
        return title

    @property
    def is_graded(self) -> bool:
        """
        Indique si l'évaluation est notée.
        """
        return self.evaluation_grade is not None

    def get_level_index_by_percentage(self, percentage: float) -> int:
        """
        Retourne le niveau de note correspondant à une note donnée.
        """
        if not (0 <= percentage <= 1):
            raise ValueError("Le pourcentage doit être compris entre 0 et 1.")
        for i, level in enumerate(self.grade_levels):
            if percentage * 100 >= level.minimum:
                return i
        raise ValueError("Aucun niveau de note ne correspond au pourcentage donné.")

    @staticmethod
    def default(*, nb_levels: int = 3) -> "Config":
        """
        Retourne une configuration par défaut.
        """
        if nb_levels < 2 or nb_levels > 5:
            raise ValueError("Le nombre de niveaux doit être entre 2 et 5.")

        levels, descriptions = Config._create_levels_with_descriptions(nb_levels)

        return Config(
            evaluation_name="Nom de l'évaluation",
            evaluation_total=100.0,
            evaluation_total_nb_decimals=0,
            evaluation_grade=None,
            evaluation_comment=None,
            student_name=None,
            student_omnivox=None,
            student_teammates=[],
            grade_levels=levels,
            criteria=Config._create_default_criteria(descriptions),
            format=Format.default(),
        )

    @staticmethod
    def _create_default_criteria(descriptions: list[str | None]) -> list[Criterion]:
        return [
                Criterion(
                    name="Critère 1",
                    total=None,
                    grade=None,
                    comment=None,
                    indicators=[
                        Indicator(
                            name="Indicateur 1.1",
                            points=None,
                            grade=None,
                            comment=None,
                            descriptors=descriptions,
                        ),
                        Indicator(
                            name="Indicateur 1.2",
                            points=None,
                            grade=None,
                            comment=None,
                            descriptors=descriptions,
                        ),
                    ],
                ),
                Criterion(
                    name="Critère 2",
                    total=None,
                    grade=None,
                    comment=None,
                    indicators=[
                        Indicator(
                            name="Indicateur 2.1",
                            points=None,
                            grade=None,
                            comment=None,
                            descriptors=descriptions,
                        ),
                        Indicator(
                            name="Indicateur 2.2",
                            points=None,
                            grade=None,
                            comment=None,
                            descriptors=descriptions,
                        ),
                    ],
                ),
            ]

    @staticmethod
    def _create_levels_with_descriptions(
            nb_levels: int
            ) -> tuple[list[GradeLevel], list[str | None]]:

        descriptions: list[str | None]
        match nb_levels:
            case 2:
                levels = [
                    GradeLevel(name="✅", maximum=100.0,
                               minimum=60.0, default_value=100.0),
                    GradeLevel(name="❌", maximum=59.0, minimum=0.0,
                               default_value=0.0),
                ]
                descriptions = [None, None]
            case 3:
                levels = [
                    GradeLevel(name="Très bien", maximum=100.0,
                               minimum=80.0, default_value=100.0),
                    GradeLevel(name="Bien", maximum=79.0,
                               minimum=60.0, default_value=70.0),
                    GradeLevel(name="Insuffisant", maximum=59.0,
                               minimum=0.0, default_value=30.0),
                ]
                descriptions = [
                    "Description du niveau très bien.",
                    "Description du niveau bien.",
                    "Description du niveau insuffisant.",
                ]
            case 4:
                levels = [
                    GradeLevel(name="Très bien", maximum=100.0,
                               minimum=85.0, default_value=100.0),
                    GradeLevel(name="Bien", maximum=84.0,
                               minimum=70.0, default_value=80.0),
                    GradeLevel(name="Passable", maximum=69.0,
                               minimum=60.0, default_value=60.0),
                    GradeLevel(name="Insuffisant", maximum=59.0,
                               minimum=0.0, default_value=30.0),
                ]
                descriptions = [
                    "Description du niveau très bien.",
                    "Description du niveau bien.",
                    "Description du niveau passable.",
                    "Description du niveau insuffisant.",
                ]
            case 5:
                levels = [
                    GradeLevel(name="Excellent", maximum=100.0,
                               minimum=90.0, default_value=100.0),
                    GradeLevel(name="Très bien", maximum=89.0,
                               minimum=80.0, default_value=80.0),
                    GradeLevel(name="Bien", maximum=79.0,
                               minimum=70.0, default_value=70.0),
                    GradeLevel(name="Passable", maximum=69.0,
                               minimum=60.0, default_value=60.0),
                    GradeLevel(name="Insuffisant", maximum=59.0,
                               minimum=0.0, default_value=30.0),
                ]
                descriptions = [
                    "Description du niveau excellent.",
                    "Description du niveau très bien.",
                    "Description du niveau bien.",
                    "Description du niveau passable.",
                    "Description du niveau insuffisant.",
                ]
            case _:
                raise ValueError("Le nombre de niveaux doit être entre 2 et 5.")

        return levels, descriptions
