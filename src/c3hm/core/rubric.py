import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import openpyxl as pyxl
from openpyxl import Workbook
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
    weight: Decimal | None = Field(
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
    total_score: Decimal = Field(
        default=100,
        ge=0
    )
    pts_precision: int = Field(
        default=0,
        ge=0
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


class Student(BaseModel):
    """
    Représente un étudiant avec un nom, prénom et code Omnivox.
    """
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    omnivox_code: str = Field(..., min_length=1)


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
    students: list[Student] = Field(
        default_factory=list,
        min_length=0
    )

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


def load_rubric_from_xlsx(
        filepath: str | Path,
         *,
         sheet_name="c3hm",
         ) -> Rubric:
    """
    Charge et initialise une grille d'évaluation à partir d'un fichier Excel.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Le fichier '{filepath}' n'existe pas.")

    wb = pyxl.load_workbook(filepath, data_only=True)
    config = read_c3hm_config_xl(wb, sheet_name=sheet_name)
    students = read_c3hm_students_xl(wb, sheet_name=sheet_name)
    config['students'] = students

    try:
        rubric = load_rubric_from_dict(config)
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du fichier : {filepath}") from e

    return rubric

def find_named_cell(wb: Workbook,
                    sheet_name: str,
                    named_cell: str) -> tuple[int, int]:
    """
    Trouve la position d'une cellule nommée dans une feuille de calcul.
    Retourne la ligne et la colonne de la cellule.
    """
    ws = wb[sheet_name]
    for dn in wb.defined_names.definedName:
        if dn.name == named_cell:
            for title, coord in dn.destinations:
                if title == sheet_name:
                    cell = ws[coord]
                    return cell.row, cell.column
    raise ValueError(f"Cellule nommée '{named_cell}' non trouvée dans la feuille '{sheet_name}'.")


def read_c3hm_students_xl(
        wb: Workbook,
        *,
        sheet_name="c3hm",
        named_cell="cthm_code_omnivox"
        ) -> list[dict]:
    """
    Lit la liste des étudiants à partir d'un fichier Excel.
    Part depuis une cellule nommée et lit vers le bas jusqu'à la première
    cellule vide. Assume que le code est dans la première colonne, le
    prénom dans la deuxième et le nom dans la troisième.

    Retourne une liste de dictionnaires.
    """
    students = []

    cell_row, cell_col = find_named_cell(wb, sheet_name, named_cell)

    # On commence à lire à la ligne suivante
    # et on lit jusqu'à la première cellule vide
    row = cell_row + 1
    ws = wb[sheet_name]
    while True:
        code_cell = ws.cell(row=row, column=cell_col)
        first_name_cell = ws.cell(row=row, column=cell_col + 1)
        last_name_cell = ws.cell(row=row, column=cell_col + 2)

        if code_cell.value is None:
            break

        d = {
            "omnivox_code": str(code_cell.value),
            "first_name": str(first_name_cell.value),
            "last_name": str(last_name_cell.value)
        }
        students.append(d)
        row += 1

    return students

def read_c3hm_config_xl(
        wb: Workbook,
        *,
        sheet_name="c3hm",
        named_cell="cthm_config_key"
        ) -> dict[str, Any]:
    """
    Lit la configuration d'une grille d'évaluation à partir d'un fichier Excel.
    Part depuis une cellule nommée et lit vers le bas jusqu'à la première
    cellule vide. Assume que la cellule nommée est dans la première colonne et
    que les valeurs sont dans la deuxième colonne.
    """
    config = {}

    cell_row, cell_col = find_named_cell(wb, sheet_name, named_cell)

    # On commence à lire à la ligne suivante
    # et on lit jusqu'à la première cellule vide
    row = cell_row + 1
    ws = wb[sheet_name]
    while True:
        key_cell = ws.cell(row=row, column=cell_col)
        value_cell = ws.cell(row=row, column=cell_col + 1)

        if key_cell.value is None:
            break

        key = str(key_cell.value)
        value = value_cell.value
        config[key] = value
        row += 1

    return config


def load_rubric_from_dict(data: dict) -> Rubric:
    """
    Charge et initialise une grille d'évaluation à partir d'un dictionnaire.

    Voir le gabarit grille_5_niveaux.xlsx pour la structure attendue.
    """

    cours = data.get("cours")
    evaluation = data.get("évaluation")
    total = data.get("total", 100)
    pts_precision = data.get("pts_precision", 0)
    scale = get_scale(data)
    thresholds = get_thresholds(data)
    if len(thresholds) != len(scale):
        raise ValueError("Le nombre de seuils doit correspondre "
                         "au nombre de niveaux du barème.")
    criteria = get_criteria(data)
    if not criteria:
        raise ValueError("Aucun critère trouvé.")
    students = get_students(data)

    grid = RubricGrid(
        scale=scale,
        criteria=criteria,
        total_score=total,
        pts_precision=pts_precision,
        thresholds=thresholds
    )

    rubric = Rubric(
        course=cours,
        evaluation=evaluation,
        grid=grid,
        students=students
    )

    rubric.validate_rubric()
    return rubric


def get_scale(d: dict[str, Any]) -> list[str]:
    """
    Retourne la liste des niveaux de barème à partir d'un dictionnaire
    ou la liste par défaut si aucun barème n'est trouvé.
    """
    scale = []
    for k in d:
        if k.startswith("B"):
            scale.append(d[k])
    if not scale:
        scale = ["Excellent", "Très bien", "Bien", "Passable", "Insuffisant"]
    return scale


def get_thresholds(d: dict[str, Any]) -> list[int]:
    """
    Retourne la liste des seuils à partir d'un dictionnaire
    ou la liste par défaut si aucun seuil n'est trouvé.
    """
    thresholds = []
    for k in d:
        if k.startswith("S"):
            thresholds.append(d[k])
    if not thresholds:
        thresholds = [100, 85, 70, 60, 0]
    return thresholds

def get_students(d: dict[str, Any]) -> list[Student]:
    """
    Retourne la liste des étudiants à partir d'un dictionnaire.
    """
    students = []
    if "students" in d:
        for student in d["students"]:
            students.append(Student(**student))
    return students

def get_criteria(d: dict[str, Any]) -> list[Criterion]:
    """
    Retourne la liste des critères à partir d'un dictionnaire.
    """
    criteria: list[Criterion] = []
    # repérer tous les IDs de critères (C1, C2, ...)
    cids = []
    for k in d:
        m = re.match(r'^(C\d+)', k)
        if m:
            cids.append(m.group(1))

    for cid in cids:
        name = d[cid]
        weight = d.get(f"{cid}_pts")

        # repérer tous les indicateurs pour ce critère
        iids = []
        for k in d:
            m = re.match(rf'^{cid}_(I\d+)', k)
            if m:
                iids.append(m.group(1))

        indicators: list[Indicator] = []
        for iid in iids:
            ind_key = f"{cid}_{iid}"
            ind_name = d[ind_key]

            # repérer tous les  descripteurs de l'indicateur
            dids = []
            for k in d:
                m = re.match(rf'^{cid}_{iid}_(D\d+)', k)
                if m:
                    desc_items.append(m.group(1))

            for
            descriptors = [v for _, v in desc_items]
            indicators.append(Indicator(name=ind_name, descriptors=descriptors))
        criteria.append(Criterion(name=name, indicators=indicators, weight=weight))
    return criteria

