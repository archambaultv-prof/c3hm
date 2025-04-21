from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from c3hm.core.utils import split_integer


class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    name: str = Field(..., min_length=1)
    descriptors: list[str] = Field(
        min_length=1
    )


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière peut être formée d'une liste d'indicateurs.
    """
    name: str = Field(..., min_length=1)
    indicators: list[Indicator] = Field(
        min_length=1
    )
    weight: int | None = Field(
        default=None,
        ge=0
    )

    def nb_indicators(self) -> int:
        """
        Retourne le nombre d'indicateurs dans le critère.
        """
        return len(self.indicators)


class RubricGrid(BaseModel):
    """
    Représente la grille d'évaluation.

    Une grille est formée d'une barème (Excellent, Très bien, ...) et d'une liste de critères.
    Il est possible d'ajouter des seuils pour chaque critère.
    """
    scale: list[str] = Field(
        default=["Excellent", "Très bien", "Bien", "Passable", "Insuffisant"],
        min_length=2
        )
    criteria: list[Criterion] = Field(..., min_length=1)
    total_score: int = Field(
        default=100,
        ge=0,
        le=100
    )
    thresholds: list[int] = Field(
        default=[100, 85, 70, 60, 0],
        min_length=2,
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


class Rubric(BaseModel):
    """
    Représente une grille d'évaluation pour un cours et une évaluation spécifiques.
    """
    course: str | None = Field(
         default=None,
         min_length=1
         )
    evaluation: str | None  = Field(
        default=None,
        min_length=1
        )
    grid: RubricGrid

    def title(self) -> str:
        """
        Retourne le titre de la grille d'évaluation.

        Le titre est formé du nom du cours et de l'évaluation, séparés par un tiret.
        """
        endash = "\u2013"
        title = "Grille d'évaluation"
        if self.evaluation:
            title += f" {endash} {self.evaluation}"
        if self.course:
            title += f" {endash} {self.course}"
        return title

    def validate_rubric(self) -> None:
        """
        Valide la grille d'évaluation.

        Vérifie que
         - le nombre de seuils correspond au nombre de niveaux du barème
         - les poids ne dépassent pas le total

        Remplit les valeurs implicites, comme des critères sans poids
        """
        # Vérification du nombre de seuils
        if len(self.grid.scale) != len(self.grid.thresholds):
            raise ValueError("Le nombre de seuils doit correspondre "
                             "au nombre de niveaux du barème.")

        # Vérification des poids
        weight_total = 0
        nb_without_weight = 0
        for criterion in self.grid.criteria:
            if criterion.weight is None:
                nb_without_weight += 1
            elif isinstance(criterion.weight, int):
                weight_total += criterion.weight
            else:
                raise ValueError(f"Le poids du critère '{criterion.name}' "
                                 f"doit être un entier positif.")
        unallocated_weight = self.grid.total_score - weight_total
        if unallocated_weight < 0:
            raise ValueError("La somme des poids des critères dépasse le total.")
        if nb_without_weight > 0:
            weights = split_integer(unallocated_weight, nb_without_weight)
            weights.reverse()
            for criterion in self.grid.criteria:
                if criterion.weight is None:
                    criterion.weight = weights.pop()


def load_rubric_from_yaml(filepath: str | Path) -> Rubric:
    """
    Charge et initialise une grille d'évaluation à partir d'un fichier YAML.
    """
    with open(filepath, encoding='utf-8') as file:
        try:
            data = yaml.safe_load(file)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement de la grille "
                             f"d'évaluation {filepath}")  from e

    if not isinstance(data, dict):
        raise ValueError(f"Le fichier {filepath} ne contient pas un dictionnaire.")

    try:
        rubric = load_rubric_from_dict(data)
    except Exception as e:
        raise ValueError(f"Erreur lors de la création de la grille "
                         f"d'évaluation {filepath}") from e

    return rubric

def load_rubric_from_dict(data: dict) -> Rubric:
    """
    Charge et initialise une grille d'évaluation à partir d'un dictionnaire.
    """

    grid_data = data.get('grille')
    if not grid_data:
        raise ValueError("Aucune grille.")
    if not isinstance(grid_data, dict):
        raise ValueError("La grille doit être un dictionnaire.")

    # Construction des critères
    criteria = []
    if not grid_data.get('critères'):
        raise ValueError("Aucun critère.")

    for idx, crit in enumerate(grid_data.get('critères')):
        if not isinstance(crit, dict):
            raise ValueError(f"Critère {idx + 1} doit être un dictionnaire.")
        if not crit.get('critère'):
            raise ValueError(f"Critère {idx + 1} sans nom ('critère:').")
        crit_name = crit['critère']
        weight = crit.get('poids')
        indicators = []
        if not crit.get('indicateurs'):
            raise ValueError("Aucun indicateur trouvé "
                             f"pour le critère {crit_name}.")
        for idx, ind in enumerate(crit.get('indicateurs')):
            if not isinstance(ind, dict):
                raise ValueError(f"Indicateur {idx + 1} doit être un dictionnaire. "
                                 f"Critère {crit_name}.")
            if not ind.get('nom'):
                raise ValueError(f"Indicateur {idx + 1} sans nom ('nom:'). "
                                 f"Critère {crit_name}.")
            if not ind.get('descripteurs'):
                raise ValueError(f"Aucun descripteur trouvé "
                                 f"pour l'indicateur {ind['nom']} du critère {crit_name}.")
            indicators.append(Indicator(
                name=ind.get('nom'),
                descriptors=ind.get('descripteurs')
            ))
        criteria.append(Criterion(
            name=crit.get('critère', 'Critère sans nom'),
            indicators=indicators,
            weight=weight
        ))

    # Création de la grille
    grid_extra_data = dict()
    if grid_data.get('barème'):
        grid_extra_data['scale'] = grid_data.get('barème')
    if grid_data.get('total'):
        grid_extra_data['total_score'] = grid_data.get('total')
    if grid_data.get('seuil'):
        grid_extra_data['thresholds'] = grid_data.get('seuil')

    rubric_grid = RubricGrid(
        criteria=criteria,
        **grid_extra_data
    )

    # Création de l'objet Rubric
    rubric_extra_data = dict()
    if data.get('cours'):
        rubric_extra_data['course'] = data.get('cours')
    if data.get('evaluation'):
        rubric_extra_data['evaluation'] = data.get('evaluation')

    rubric= Rubric(
        grid=rubric_grid,
        **rubric_extra_data
    )

    rubric.validate_rubric()
    return rubric

