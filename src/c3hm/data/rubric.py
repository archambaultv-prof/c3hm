from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from c3hm.data.criterion import Criterion
from c3hm.data.format import Format
from c3hm.utils.decimal import (
    decimal_to_number,
    is_multiple_of_quantum,
    split_decimal,
)

GradeLevels = list[str]

GradeThresholds = list[tuple[Decimal, Decimal, Decimal]]

CTHM_OMNIVOX = "cthm_omnivox"
CTHM_GLOBAL_COMMENT = "cthm_global_comment"


class Rubric(BaseModel):
    """
    Représente la grille d'évaluation.

    Une grille est formée de niveaux (Excellent, Très bien, ...) et d'une liste de critères.
    Il est possible d'ajouter des seuils pour chaque critère.
    """
    precision: Decimal = Field(
        default=Decimal("1"),
        description="Précision de la note totale. Par défaut, 1."
    )

    grade_levels: list[str] = Field(..., min_length=1)

    grade_thresholds : list[tuple[Decimal, Decimal, Decimal]]

    default_descriptors: list[str] = Field(..., min_length=1,)

    criteria: list[Criterion] = Field(..., min_length=1)

    format: Format

    def max_grade(self) -> Decimal:
        """
        Retourne la note maximale de la grille d'évaluation.
        """
        if not self.grade_thresholds:
            raise ValueError("La grille d'évaluation n'a pas de seuils définis.")
        return self.grade_thresholds[0][0]

    def threshold_default(self, i: int) -> Decimal:
        """
        Retourne le seuil par défaut pour le niveau i.
        """
        if i < 0 or i >= len(self.grade_levels):
            raise IndexError(f"Index {i} hors des limites pour les niveaux de la grille.")
        return self.grade_thresholds[i][2]

    def threshold_str(self, i: int) -> str:
        """
        Retourne une chaîne de caractères représentant le seuil pour le niveau i.
        """
        if i < 0 or i >= len(self.grade_levels):
            raise IndexError(f"Index {i} hors des limites pour les niveaux de la grille.")
        max_grade = self.grade_thresholds[i][0]
        min_grade = self.grade_thresholds[i][1]
        if min_grade == max_grade:
            return f"{min_grade}"
        else:
            if min_grade == Decimal("0"):
                return f"{max_grade} et moins"
            return f"{max_grade} à {min_grade}"

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la grille d'évaluation.
        """
        return {
            "précision": decimal_to_number(self.precision),
            "niveaux": self.grade_levels.copy(),
            "seuils par niveau": map(
                lambda tup: map(decimal_to_number, tup),
                self.grade_thresholds
            ),
            "descripteurs par défaut": self.default_descriptors.copy(),
            "critères": [criterion.to_dict() for criterion in self.criteria],
            "format": self.format.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
        """
        Crée une instance de Rubric à partir d'un dictionnaire.
        """
        return cls(
            precision=data.get("précision", Decimal("1")),
            grade_levels=data["niveaux"],
            grade_thresholds=data["seuils par niveau"],
            default_descriptors=data.get("descripteurs par défaut", []),
            criteria=[Criterion.from_dict(criterion) for criterion in data["critères"]],
            format=Format.from_dict(data["format"]),
        )

    def nb_criteria(self) -> int:
        """
        Retourne le nombre de critères dans la grille.
        """
        return len(self.criteria)

    def validate(self) -> None: # type: ignore
        """
        Valide la grille d'évaluation. Remplace les valeurs manquantes par
        des valeurs par défaut.
        """
        _validate_criteria_percentage(self)
        _validate_thresholds(self)
        _validate_criteria(self)


    def to_yaml(self, filepath: str | Path) -> None:
        """
        Sauvegarde la grille d'évaluation au format YAML.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True,
                      sort_keys=False)

    def copy(self) -> "Rubric": # type: ignore
        """
        Retourne une copie de la grille d'évaluation.
        """
        return Rubric(
            precision=self.precision,
            grade_levels=self.grade_levels.copy(),
            grade_thresholds=self.grade_thresholds.copy(),
            default_descriptors=self.default_descriptors.copy(),
            criteria=[criterion.copy() for criterion in self.criteria],
            format=self.format.copy()
        )


def _validate_criteria_percentage(rubric: Rubric) -> None:
    total = Decimal(100)
    nb_missing = len([criterion for criterion in rubric.criteria if criterion.percentage is None])
    criteria_total = Decimal(0)
    for criterion in rubric.criteria:
        if criterion.percentage:
            if not is_multiple_of_quantum(criterion.percentage, Decimal(1)):
                raise ValueError(
                    f"Le pourcentage du critère '{criterion.name}' "
                    f"({criterion.percentage}) n'est pas un multiple de 1%."
                )
            criteria_total += criterion.percentage
    if nb_missing == 0:
        if criteria_total != total:
            raise ValueError(
                "La somme des pourcentages des critères n'est pas égale à 100%"
            )
    else:
        # Répartition du reste entre les critères non définis
        rest = total - criteria_total
        if rest <= 0:
            raise ValueError(
                "La somme des pourcentages des critères est supérieure à 100%"
            )
        parts = split_decimal(rest, nb_missing, Decimal(1))
        for i, criterion in enumerate(rubric.criteria):
            if criterion.percentage is None:
                criterion.percentage = parts[i]

def _validate_indicators_percentage(criteriron: Criterion) -> None:
    if criteriron.percentage is None:
        raise ValueError(
            f"Le critère '{criteriron.name}' n'a pas de pourcentage défini."
        )
    total = criteriron.percentage
    nb_missing = len([ind for ind in criteriron.indicators if ind.percentage is None])
    indicators_total = Decimal(0)
    for indicator in criteriron.indicators:
        if indicator.percentage:
            if not is_multiple_of_quantum(indicator.percentage, Decimal(1)):
                raise ValueError(
                    f"Le pourcentage de l'indicateur '{indicator.name}' "
                    f"({indicator.percentage}) n'est pas un multiple de 1%."
                )
            indicators_total += indicator.percentage
    if nb_missing == 0:
        if indicators_total != total:
            raise ValueError(
                "La somme des pourcentages des critères n'est pas égale au pourcentage du critère."
            )
    else:
        # Répartition du reste entre les critères non définis
        rest = total - indicators_total
        if rest <= 0:
            raise ValueError(
                "La somme des pourcentages des indicateurs est supérieure au pourcentage"
                " du critère."
            )
        parts = split_decimal(rest, nb_missing, Decimal(1))
        for i, indicator in enumerate(criteriron.indicators):
            if indicator.percentage is None:
                indicator.percentage = parts[i]

def _validate_thresholds(rubric: Rubric) -> None:
    """
    Valide les seuils de la grille d'évaluation.
    """
    nb_of_levels = len(rubric.grade_levels)

    # Vérification des seuils (max, min, défaut)
    if len(rubric.grade_thresholds) != nb_of_levels:
        raise ValueError(
            "Le nombre de seuils ne correspond pas au nombre de niveaux "
            f"({nb_of_levels})."
        )
    for i, (min_threshold, max_threshold, default_threshold) in enumerate(
        rubric.grade_thresholds
    ):
        if min_threshold >= max_threshold:
            raise ValueError(
                f"Le seuil minimum ({min_threshold}) est supérieur ou égal au seuil "
                f"maximum ({max_threshold}) pour le niveau {rubric.grade_levels[i]}."
            )
        if default_threshold < min_threshold or default_threshold > max_threshold:
            raise ValueError(
                f"Le seuil par défaut ({default_threshold}) n'est pas compris entre "
                f"le seuil minimum ({min_threshold}) et le seuil maximum "
                f"({max_threshold}) pour le niveau {rubric.grade_levels[i]}."
            )

def _validate_criteria(rubric: Rubric) -> None:
    nb_of_levels = len(rubric.grade_levels)
    seen_xl_ids = set(CTHM_OMNIVOX)  # cthm_omnivox est réservé pour le code omnivox
    for c, criterion in enumerate(rubric.criteria):

        if criterion.xl_cell_id is None:
            criterion.xl_cell_id = f"cthm_C{c+1}"
        if criterion.xl_cell_id in seen_xl_ids:
            raise ValueError(
                f"Le critère '{criterion.name}' a un identifiant de cellule "
                f"Excel dupliqué : {criterion.xl_cell_id}."
            )
        seen_xl_ids.add(criterion.xl_cell_id)

        # Vérification des indicateurs
        if not criterion.indicators:
            raise ValueError(f"Le critère '{criterion.name}' n'a pas d'indicateurs.")
        _validate_indicators_percentage(criterion)
        for i, indicator in enumerate(criterion.indicators):
            if indicator.xl_cell_id is None:
                prefix = criterion.xl_cell_id
                indicator.xl_cell_id = f"{prefix}_I{i+1}"
            if indicator.xl_cell_id in seen_xl_ids:
                raise ValueError(
                    f"L'indicateur '{indicator.name}' du critère '{criterion.name}' "
                    f"a un identifiant de cellule Excel dupliqué : {indicator.xl_cell_id}."
                )
            seen_xl_ids.add(indicator.xl_cell_id)

            if indicator.descriptors:
                if len(indicator.descriptors) != nb_of_levels:
                    raise ValueError(
                        f"Le nombre de descripteurs pour l'indicateur '{indicator.name}' "
                        f"du critère '{criterion.name}' ne correspond pas au nombre de niveaux "
                        f"({nb_of_levels})."
                    )
            else:
                if not rubric.default_descriptors:
                    raise ValueError(
                        f"L'indicateur '{indicator.name}' du critère '{criterion.name}' "
                        "n'a pas de descripteurs par défaut définis."
                    )
                indicator.descriptors = rubric.default_descriptors.copy()
