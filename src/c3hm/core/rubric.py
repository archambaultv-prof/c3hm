from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Indicator(BaseModel):
    """
    Représente un indicateur d'évaluation pour un critère donné.
    """
    name: str = Field(..., min_length=1)
    descriptors: list[str]


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière peut être formée d'une liste d'indicateurs.
    """
    name: str = Field(..., min_length=1)
    indicators: list[Indicator] = Field(
        min_length=1
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
    scale: list[str] = Field(..., min_length=2)
    criteria: list[Criterion] = Field(..., min_length=1)
    thresholds: list[int] | None = Field(
        default=None
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


def load_rubric_from_yaml(filepath: str | Path) -> Rubric:
    """
    Charge une grille d'évaluation à partir d'un fichier YAML.

    Les valeurs optionnelles non spécifiées dans le fichier YAML seront
    instanciées avec des valeurs par défaut spécifiées dans les modèles Pydantic.
    """
    with open(filepath, encoding='utf-8') as file:
        try:
            data: dict = yaml.safe_load(file)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement de la grille "
                             f"d'évaluation {filepath}")  from e

    # Extraction des données de la grille
    grid_data: dict = data.get('grille')
    if not grid_data:
        raise ValueError(f"Aucune grille trouvée dans le fichier {filepath}.")
    scale = grid_data.get('barème')
    if not scale:
        raise ValueError(f"Aucun barème trouvé dans le fichier {filepath}.")
    thresholds = grid_data.get('seuil')

    # Construction des critères
    criteria = []
    if not grid_data.get('critères'):
        raise ValueError(f"Aucun critère trouvé dans le fichier {filepath}.")

    for idx, crit in enumerate(grid_data.get('critères')):
        if not isinstance(crit, dict):
            raise ValueError(f"Critère {idx + 1} doit être un dictionnaire. Fichier {filepath}")
        if not crit.get('critère'):
            raise ValueError(f"Critère {idx + 1} sans nom ('critère:'). Fichier {filepath}.")
        crit_name = crit['critère']
        indicators = []
        if not crit.get('indicateurs'):
            raise ValueError(f"Aucun indicateur trouvé dans le fichier {filepath} "
                             f"pour le critère {crit_name}.")
        for idx, ind in enumerate(crit.get('indicateurs')):
            if not isinstance(ind, dict):
                raise ValueError(f"Indicateur {idx + 1} doit être un dictionnaire. "
                                 f"Critère {crit_name}. Fichier {filepath}")
            indicators.append(Indicator(
                name=ind.get('nom'),
                descriptors=ind.get('descripteurs')
            ))
        criteria.append(Criterion(
            name=crit.get('critère', 'Critère sans nom'),
            indicators=indicators
        ))

    # Création de la grille
    rubric_grid = RubricGrid(
        scale=scale,
        criteria=criteria,
        thresholds=thresholds
    )

    # Création de l'objet Rubric
    return Rubric(
        course=data.get('cours'),
        evaluation=data.get('evaluation'),
        grid=rubric_grid
    )

