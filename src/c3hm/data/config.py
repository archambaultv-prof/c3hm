from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.criterion import Criterion
from c3hm.data.format import Format
from c3hm.data.grade_level import GradeLevel
from c3hm.data.indicator import Indicator

NonNegFloat = Annotated[float, Field(ge=0.0)]

class Config(BaseModel):
    """
    Représente la configuration qui est utilisée par générer la grille de
    correction et les rétroactions.
    """
    model_config = ConfigDict(extra="forbid")

    evaluation_name: str = Field(..., min_length=1)
    evaluation_total: float | None = Field(..., gt=0)
    evaluation_total_nb_decimals: int = Field(0, ge=0)
    evaluation_grade: NonNegFloat | str | None = Field(None)
    evaluation_comment: str | None = Field(None, min_length=1)

    student_first_name: str | None = Field(None, min_length=1)
    student_last_name: str | None = Field(None, min_length=1)
    student_omnivox: str | None = Field(None, min_length=1)
    student_teammates: list[str] = Field(default_factory=list)

    grade_levels: list[GradeLevel]

    criteria: list[Criterion]

    format: Format = Field(default_factory=Format.default)

    def get_total(self) -> float:
        """
        Retourne le total des points de l'évaluation.
        """
        if self.evaluation_total is None:
            raise ValueError("Le total des points de l'évaluation n'est pas défini.")
        return self.evaluation_total

    def get_grade(self) -> float:
        """
        Retourne la note du critère.
        """
        if self.evaluation_grade is None or isinstance(self.evaluation_grade, str):
            raise ValueError("La note du critère n'est pas définie.")
        return self.evaluation_grade

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

    def get_student_full_name(self) -> str:
        """
        Retourne le nom complet de l'étudiant.
        """
        if self.student_first_name is None or self.student_last_name is None:
            raise ValueError("Le nom de l'étudiant n'est pas défini.")
        return f"{self.student_first_name} {self.student_last_name}"

    def get_level_index_by_percentage(self, percentage: float) -> int:
        """
        Retourne le niveau de note correspondant à une note donnée.
        """
        if not (0 <= percentage <= 1):
            raise ValueError(f"Le pourcentage ('{percentage}') doit être compris entre 0 et 1.")
        for i, level in enumerate(self.grade_levels):
            if percentage * 100 >= level.minimum:
                return i
        raise ValueError("Aucun niveau de note ne correspond au pourcentage donné.")

    def get_level_by_name(self, name: str) -> GradeLevel:
        """
        Retourne le niveau de note correspondant à un nom donné.
        """
        for level in self.grade_levels:
            if level.name == name:
                return level
        raise ValueError(f"Aucun niveau de note ne correspond au nom '{name}'.")

    def yaml_dump(self, output_path: Path) -> None:
        """
        Retourne la configuration au format YAML.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(mode="json"), f,
                    sort_keys=False, allow_unicode=True,
                    indent=2)

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
            student_first_name=None,
            student_last_name=None,
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
                descriptions = ["", ""]
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
