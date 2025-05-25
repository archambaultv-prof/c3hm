from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from c3hm.data.criterion import Criterion
from c3hm.data.format import Format
from c3hm.utils import decimal_to_number, round_to_nearest_quantum, split_decimal

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
    total: Decimal | None = Field(..., gt=0)

    total_precision: Decimal = Field(
        default=Decimal("1"),
        description="Précision de la note totale. Par défaut, 1."
    )

    grade_levels: list[str] = Field(..., min_length=1)

    grade_thresholds : list[tuple[Decimal, Decimal, Decimal]]

    default_descriptors: list[str] = Field(..., min_length=1,)

    criteria: list[Criterion] = Field(..., min_length=1)

    format: Format

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la grille d'évaluation.
        """
        return {
            "total": decimal_to_number(self.total) if self.total is not None else None,
            "total précision": decimal_to_number(self.total_precision),
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
            total=data["total"],
            total_precision=data.get("total précision", Decimal("1")),
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


    def nb_columns(self) -> int:
        """
        Retourne le nombre total de colonnes dans la grille.

        Cela inclut une colonne pour les critères/descripteurs et une colonne
        pour chaque niveau de barème.
        """
        return 1 + len(self.grade_levels)

    def validate(self) -> None: # type: ignore
        """
        Valide la grille d'évaluation. Remplace les valeurs manquantes par
        des valeurs par défaut.
        """
        _validate_total(self)
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
            total=self.total,
            total_precision=self.total_precision,
            grade_levels=self.grade_levels.copy(),
            grade_thresholds=self.grade_thresholds.copy(),
            default_descriptors=self.default_descriptors.copy(),
            criteria=[criterion.copy() for criterion in self.criteria],
            format=self.format.copy()
        )


def _validate_total(rubric: Rubric) -> None:
    # Vérification des totaux
    # Si total est None, on le remplace par la somme des totaux des critères
    # Si total n'est pas None:
    #   - on vérifie que la somme des totaux des critères est égale à total s'ils
    #     sont tous définis
    #   - on vérifie que la somme des totaux des critères est inférieure à total
    #     s'ils ne sont pas tous définis et on répartie également le reste entre les critères
    #     non définis
    for c in rubric.criteria:
        if c.total:
            x = round_to_nearest_quantum(c.total, rubric.total_precision)
            if x != c.total:
                raise ValueError(
                    f"Le total du critère '{c.name}' ({c.total}) n'est pas un multiple de "
                    f"la précision totale ({rubric.total_precision})."
                )
    nb_missing = len([criterion for criterion in rubric.criteria if criterion.total is None])
    criteria_total = sum((criterion.total for criterion in rubric.criteria
                            if criterion.total is not None),
                            start=Decimal(0))
    if rubric.total is None:
        if nb_missing != 0:
            raise ValueError(
                "La grille d'évaluation n'a pas de total défini. "
                "Tous les critères doivent avoir un total défini."
            )
        rubric.total = criteria_total
    else:
        if nb_missing == 0:
            if criteria_total != rubric.total:
                raise ValueError(
                    "La somme des totaux des critères ne correspond pas au total de la grille."
                )
        else:
            # Répartition du reste entre les critères non définis
            rest = rubric.total - criteria_total
            if rest <= 0:
                raise ValueError(
                    "La somme des totaux des critères est supérieure "
                    "ou égale au total de la grille."
                )
            parts = split_decimal(rest, nb_missing, rubric.total_precision)
            for i, criterion in enumerate(rubric.criteria):
                if criterion.total is None:
                    criterion.total = parts[i]


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
