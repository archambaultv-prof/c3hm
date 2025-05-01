from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from c3hm.utils import decimal_to_number, is_multiple_of_quantum, split_decimal


class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    name: str = Field(..., min_length=1)
    descriptors: list[str]
    weight: Decimal = Field(
        default=1,
        ge=0,
        description="Poids relatif de l'indicateur dans le critère."
    )
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
            "poids relatif": decimal_to_number(self.weight),
            "descripteurs": self.descriptors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Indicator":
        """
        Crée une instance de Indicator à partir d'un dictionnaire.
        """
        return cls(
            name=data["nom"],
            weight=data["poids relatif"],
            descriptors=data["descripteurs"],
        )

class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière peut être formée d'une liste d'indicateurs.
    """
    name: str = Field(..., min_length=1)
    indicators: list[Indicator]
    points: Decimal | None = Field(
        default=None,
        ge=Decimal(0)
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
            "pondération": decimal_to_number(self.points) if self.points is not None else None,
            "indicateurs": [indicator.to_dict() for indicator in self.indicators],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        """
        Crée une instance de Criterion à partir d'un dictionnaire.
        """
        return cls(
            name=data["critère"],
            points=data["pondération"],
            indicators=[Indicator.from_dict(ind) for ind in data["indicateurs"]],
        )

class EvaluationLevel(BaseModel):
    """
    Représente un niveau de la grille d'évaluation.
    """
    name: str = Field(..., min_length=1)
    threshold: Decimal = Field(
        ge=Decimal(0),
        description="Seuil minimum pour atteindre ce niveau."
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant le niveau.
        """
        return {
            "nom": self.name,
            "seuil": decimal_to_number(self.threshold),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationLevel":
        """
        Crée une instance de EvaluationLevel à partir d'un dictionnaire.
        """
        return cls(
            name=data["nom"],
            threshold=data["seuil"],
        )

class Scale(BaseModel):
    """
    Représente la liste des niveaux de la grille d'évaluation.
    """
    levels: list[EvaluationLevel] = Field(..., min_length=1)
    precision: Decimal = Field(
        default=Decimal(1),
        ge=0
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la liste des niveaux.
        """
        return {
            "niveaux": [level.to_dict() for level in self.levels],
            "précision": decimal_to_number(self.precision),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scale":
        """
        Crée une instance de Scale à partir d'un dictionnaire.
        """
        return cls(
            levels=[EvaluationLevel.from_dict(level) for level in data["niveaux"]],
            precision=data["précision"],
        )

    def __len__(self) -> int:
        """
        Retourne le nombre de niveaux dans la grille.
        """
        return len(self.levels)

    def __getitem__(self, index: int) -> EvaluationLevel:
        """
        Retourne le niveau à l'index donné.
        """
        return self.levels[index]

    def __iter__(self):
        """
        Retourne un itérateur sur les niveaux de la grille.
        """
        return iter(self.levels)

    def __contains__(self, item: str) -> bool:
        """
        Vérifie si un niveau donné est dans la grille.
        """
        return any(level.name == item for level in self.levels)

class Rubric(BaseModel):
    """
    Représente la grille d'évaluation.

    Une grille est formée de niveaux (Excellent, Très bien, ...) et d'une liste de critères.
    Il est possible d'ajouter des seuils pour chaque critère.
    """
    scale: Scale

    criteria: list[Criterion] = Field(..., min_length=1)

    pts_total: Decimal = Field(
        default=100,
        ge=0
    )
    pts_precision: Decimal = Field(
        default=0,
        ge=0
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la grille d'évaluation.
        """
        return {
            "échelle": self.scale.to_dict(),
            "critères": [criterion.to_dict() for criterion in self.criteria],
            "total": decimal_to_number(self.pts_total),
            "précision": decimal_to_number(self.pts_precision),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
        """
        Crée une instance de Rubric à partir d'un dictionnaire.
        """
        return cls(
            scale=Scale.from_dict(data["échelle"]),
            criteria=[Criterion.from_dict(criterion) for criterion in data["critères"]],
            pts_total=data["total"],
            pts_precision=data["précision"],
        )

    def nb_criteria(self) -> int:
        """
        Retourne le nombre de critères dans la grille.
        """
        return len(self.criteria)

    def nb_rows(self) -> int:
        """
        Retourne le nombre total de lignes dans la grille.

        Cela inclut une ligne pour le barème, une ligne pour chaque critère
        et une ligne pour chaque indicateur de chaque critère.
        """
        return 1 + self.nb_criteria() + sum(
            criterion.nb_indicators() for criterion in self.criteria
        )

    def nb_columns(self) -> int:
        """
        Retourne le nombre total de colonnes dans la grille.

        Cela inclut une colonne pour les critères/descripteurs et une colonne
        pour chaque niveau de barème.
        """
        return 1 + len(self.scale)

    def validate(self) -> None:
        """
        Valide la grille d'évaluation.

        - Vérifie que les poids des critères sont valides
        - Vérifie que la somme des poids est égale au total
        - Vérifie les xl_cell_id des critères et indicateurs
        - Vérifie la consistance des descripteurs et indicateurs

        """
        # Vérification des poids
        weight_total = Decimal(0)
        nb_without_weight = 0
        for criterion in self.criteria:
            if criterion.points is None:
                nb_without_weight += 1
            else:
                # Verification si precision est respectée
                if not is_multiple_of_quantum(criterion.points, self.pts_precision):
                    raise ValueError(
                        f"Le poids du critère '{criterion.name}' "
                        f"doit être un multiple de {self.pts_precision}."
                        f"Ajuster le poids ou la précision."
                    )
                weight_total += criterion.points
        unallocated_weight = self.pts_total - weight_total
        if unallocated_weight < 0:
            raise ValueError("La somme des poids des critères dépasse le total.")
        if nb_without_weight > 0:
            weights = split_decimal(unallocated_weight, nb_without_weight, self.pts_precision)
            weights.reverse()
            for criterion in self.criteria:
                if criterion.points is None:
                    criterion.points = weights.pop()

        # Vérification des descripteurs et indicateurs
        for c, criterion in enumerate(self.criteria):
            if not criterion.indicators:
                raise ValueError(f"Le critère '{criterion.name}' n'a pas d'indicateurs.")
            if criterion.xl_cell_id is None:
                criterion.xl_cell_id = f"cthm_C{c+1}"
            for i, indicator in enumerate(criterion.indicators):
                if indicator.xl_cell_id is None:
                    indicator.xl_cell_id = f"cthm_C{c+1}_I{i+1}"
                if len(indicator.descriptors) != len(self.scale):
                    raise ValueError(
                        f"Le nombre de descripteurs pour l'indicateur '{indicator.name}' "
                        f"doit correspondre au nombre de niveaux du barème."
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
