from decimal import Decimal
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from c3hm.utils import decimal_to_number

GradeLevels = list[str]

GradeWeight = Decimal | list[Decimal] | dict[str, Decimal]

GradeWeights = list[GradeWeight]

CTHM_OMNIVOX = "cthm_omnivox"

def max_grade_weight(grade_weight: GradeWeight) -> Decimal:
    """
    Retourne la meilleure note possible pour ce niveau.
    """
    if isinstance(grade_weight, list):
        return max(grade_weight)
    elif isinstance(grade_weight, dict):
        return max(grade_weight.values())
    elif isinstance(grade_weight, Decimal):
        return grade_weight
    else:
        raise TypeError("Le poids de la note doit être un Decimal, une liste ou un dictionnaire.")

def min_grade_weight(grade_weight: GradeWeight) -> Decimal:
    """
    Retourne la meilleure note possible pour ce niveau.
    """
    if isinstance(grade_weight, list):
        return min(grade_weight)
    elif isinstance(grade_weight, dict):
        return min(grade_weight.values())
    elif isinstance(grade_weight, Decimal):
        return grade_weight
    else:
        raise TypeError("Le poids de la note doit être un Decimal, une liste ou un dictionnaire.")

def grade_weights_to_yaml(grade_weights: GradeWeights | None):
    """
    Convertit les Decimal en nombres entier ou flottant pour éviter d'avoir des
    nombres flottants du style 1.0
    """
    if grade_weights is None:
        return None
    ls = []
    for weight in grade_weights:
        if isinstance(weight, list):
            ls.append([decimal_to_number(w) for w in weight])
        elif isinstance(weight, dict):
            ls.append({key: decimal_to_number(value) for key, value in weight.items()})
        else:
            ls.append(decimal_to_number(weight))
    return ls

class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    name: str = Field(..., min_length=1)
    descriptors: list[str]
    grade_weights: GradeWeights | None
    xl_cell_id: str | None = Field(
        default=None,
        description="Identifiant de la cellule dans le fichier Excel pour la correction.",
        min_length=1
    )

    def xl_grade_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour la note de l'indicateur.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_grade"

    def xl_comment_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour le commentaire de l'indicateur.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_comment"

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant l'indicateur.
        """
        return {
            "nom": self.name,
            "xl id": self.xl_cell_id,
            "pondération": grade_weights_to_yaml(self.grade_weights),
            "descripteurs": self.descriptors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Indicator":
        """
        Crée une instance de Indicator à partir d'un dictionnaire.
        """
        return cls(
            name=data["nom"],
            xl_cell_id=data.get("xl id"),
            grade_weights=data.get("pondération"),
            descriptors=data.get("descripteurs", []),
        )

    def copy(self) -> "Indicator":
        """
        Retourne une copie de l'indicateur.
        """
        if isinstance(self.grade_weights, list | dict):
            gw = self.grade_weights.copy()
        else:
            gw = self.grade_weights

        return Indicator(
            name=self.name,
            xl_cell_id=self.xl_cell_id,
            grade_weights=gw,
            descriptors=self.descriptors.copy(),
        )

class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    name: str = Field(..., min_length=1)
    indicators: list[Indicator] = Field(..., min_length=1)
    default_grade_weights: GradeWeights | None
    total: Decimal = Field(..., gt=Decimal(0)
    )
    total_precision: Decimal = Field(
        default=Decimal("1"),
        description="Précision de la note du critère. Par défaut, 1."
    )
    xl_cell_id: str | None = Field(
        default=None,
        description="Identifiant de la cellule dans le fichier Excel pour la correction.",
        min_length=1
    )

    def xl_grade_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour la note du critère.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_grade"

    def xl_comment_cell_id(self) -> str:
        """
        Retourne l'identifiant de la cellule pour le commentaire du critère.
        """
        if self.xl_cell_id is None:
            raise ValueError("xl_cell_id n'est pas défini.")
        return f"{self.xl_cell_id}_comment"

    def nb_indicators(self) -> int:
        """
        Retourne le nombre d'indicateurs dans le critère.
        """
        return len(self.indicators)

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le critère.
        """
        return {
            "critère": self.name,
            "xl id": self.xl_cell_id,
            "pondération par défaut": grade_weights_to_yaml(self.default_grade_weights),
            "indicateurs": [indicator.to_dict() for indicator in self.indicators],
            "total": decimal_to_number(self.total),
            "total précision": decimal_to_number(self.total_precision),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        """
        Crée une instance de Criterion à partir d'un dictionnaire.
        """
        return cls(
            name=data["critère"],
            total=data["total"],
            total_precision=data.get("total précision", Decimal("1")),
            indicators=[Indicator.from_dict(ind) for ind in data["indicateurs"]],
            xl_cell_id=data.get("xl id"),
            default_grade_weights=data.get("pondération par défaut"),
        )

    def copy(self) -> "Criterion":
        """
        Retourne une copie du critère.
        """
        if isinstance(self.default_grade_weights, list | dict):
            gw = self.default_grade_weights.copy()
        else:
            gw = self.default_grade_weights

        return Criterion(
            name=self.name,
            xl_cell_id=self.xl_cell_id,
            total=self.total,
            total_precision=self.total_precision,
            indicators=[indicator.copy() for indicator in self.indicators],
            default_grade_weights=gw,
        )

class Format(BaseModel):
    """
    Représente le format de la grille d'évaluation.
    """
    orientation: None | Literal["portrait", "paysage"] = Field(
        default=None,
        description="Orientation de la grille d'évaluation. Peut être 'portrait' ou 'paysage'."
    )
    hide_indicators: bool = Field(
        default=False,
        description="Indique si les indicateurs doivent être masqués dans la grille d'évaluation."
    )
    columns_width: list[float | None] = Field(
        default_factory=list,
        description="Largeur des colonnes de la grille d'évaluation. "
                    "La première colonne est pour les critères, "
                    "les autres pour les niveaux de barème."
    )
    hide_indicators_weight: bool = Field(
        default=False,
        description=("Indique si les poids des indicateurs doivent être masqués "
                     "dans la grille d'évaluation.")
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le format de la grille d'évaluation.
        """
        return {
            "orientation": self.orientation,
            "masquer les indicateurs": self.hide_indicators,
            "masquer la pondération des indicateurs": self.hide_indicators_weight,
            "largeur des colonnes": self.columns_width,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Format":
        """
        Crée une instance de Format à partir d'un dictionnaire.
        """
        return cls(
            orientation=data.get("orientation"),
            hide_indicators=data.get("masquer les indicateurs", False),
            hide_indicators_weight=data.get("masquer la pondération des indicateurs", False),
            column_width=data.get("largeur des colonnes", []),
        )

    def copy(self) -> "Format":
        """
        Retourne une copie du format.
        """
        return Format(
            orientation=self.orientation,
            hide_indicators=self.hide_indicators,
            hide_indicators_weight=self.hide_indicators_weight,
            columns_width=self.columns_width.copy(),
        )

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

    grade_levels: GradeLevels = Field(..., min_length=1)

    default_grade_weights: GradeWeights | None

    criteria: list[Criterion] = Field(..., min_length=1)

    format: Format

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la grille d'évaluation.
        """
        return {
            "total": decimal_to_number(self.total),
            "total précision": decimal_to_number(self.total_precision),
            "niveaux": self.grade_levels,
            "pondération par défaut": grade_weights_to_yaml(self.default_grade_weights),
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
            default_grade_weights=data.get("pondération par défaut"),
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

    def validate(self) -> None:
        """
        Valide la grille d'évaluation. Remplace les valeurs manquantes par
        des valeurs par défaut.
        """
        # Vérification des totaux
        computed_total = sum(
            criterion.total for criterion in self.criteria if criterion.total is not None
        )
        if self.total is None:
            self.total = computed_total
        elif computed_total != self.total:
            raise ValueError(
                f"La somme des poids des critères ({computed_total}) "
                f"ne correspond pas au total ({self.total})."
            )

        nb_of_levels = len(self.grade_levels)

        # Vérification de la pondération par défaut
        if (self.default_grade_weights is not None and
            len(self.default_grade_weights) != nb_of_levels):
                raise ValueError(
                    "La pondération par défaut de la grille "
                    f"ne correspond pas au nombre de niveaux ({nb_of_levels})."
                )

        # Vérification largeur des colonnes
        if self.format.columns_width and len(self.format.columns_width) != nb_of_levels + 1:
            raise ValueError(
                "La largeur des colonnes ne correspond pas au nombre de niveaux + 1"
                f"({nb_of_levels + 1})."
            )

        # Vérification des critères
        seen_xl_ids = set(CTHM_OMNIVOX)  # cthm_omnivox est réservé pour le code omnivox
        for c, criterion in enumerate(self.criteria):
            # Vérification de la pondération par défaut du critère si elle existe
            # sinon on lui assigne la pondération par défaut de la grille si elle existe
            if criterion.default_grade_weights is not None:
                if len(criterion.default_grade_weights) != nb_of_levels:
                    raise ValueError(
                        f"La pondération par défaut pour le critère '{criterion.name}' "
                        f"ne correspond pas au nombre de niveaux ({nb_of_levels})."
                    )
            elif self.default_grade_weights:
                    criterion.default_grade_weights = self.default_grade_weights

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

                if indicator.grade_weights is None:
                    if criterion.default_grade_weights:
                        indicator.grade_weights = criterion.default_grade_weights
                    else:
                        raise ValueError(
                            f"L'indicateur '{indicator.name}' du critère '{criterion.name}' "
                            "n'a pas de pondération. Aucune pondération par défaut n'est "
                            "définie pour le critère ou la grille."
                        )
                if (indicator.descriptors and
                    len(indicator.descriptors) != nb_of_levels):
                    raise ValueError(
                        f"Le nombre de descripteurs pour l'indicateur '{indicator.name}' "
                        f"du critère '{criterion.name}' ne correspond pas au nombre de niveaux "
                        f"({nb_of_levels})."
                    )

    def to_yaml(self, filepath: str | Path) -> None:
        """
        Sauvegarde la grille d'évaluation au format YAML.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True,
                      sort_keys=False)

    def copy(self) -> "Rubric":
        """
        Retourne une copie de la grille d'évaluation.
        """
        return Rubric(
            total=self.total,
            total_precision=self.total_precision,
            grade_levels=self.grade_levels.copy(),
            default_grade_weights= self.default_grade_weights.copy()
                                    if self.default_grade_weights else None,
            criteria=[criterion.copy() for criterion in self.criteria],
            format=self.format.copy(),
        )
