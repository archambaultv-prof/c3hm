from decimal import Decimal
from pathlib import Path
from typing import Any

import openpyxl
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.generate_rubric import generate_rubric
from c3hm.data.config import Config
from c3hm.data.rubric import CTHM_GLOBAL_COMMENT, CTHM_OMNIVOX
from c3hm.utils import round_to_nearest_quantum


def grades_from_wb(
    wb: Workbook,
    config: Config,
) -> list[dict[str, Any]]:
    """
    Lit le fichier Excel et retourne une liste de dictionnaires contenant
    les informations sur les grilles d'évaluation.
    Chaque dictionnaire contient les informations suivantes :
    - omnivox_code : le code omnivox de l'étudiant. Clé : cthm_omnivox
    - les notes et commentaires pour chaque critère et indicateur.
      Clé : le xl_cell_id_[grade|comment]
    """
    graded_rubrics = []

    for ws in wb.worksheets:
        # Test si on a un nom de cellule "cthm_omnivox" dans la feuille
        cell = find_named_cell(ws, CTHM_OMNIVOX)
        if cell is None:
            continue
        gr = grades_from_ws(ws, config)
        graded_rubrics.append(gr)

    return graded_rubrics


def find_named_cell(ws: Worksheet, named_cell: str) -> Cell | None:
    """
    Trouve une cellule nommée dans une feuille de calcul.
    Retourne la cellule si elle existe, sinon None.
    """
    # Vérifie si la cellule nommée existe
    if named_cell in ws.defined_names:
        defn = ws.defined_names[named_cell]
    else:
        return None

    for title, coord in defn.destinations:
        if title == ws.title:
            cell = ws[coord]
            return cell

    return None


def grades_from_ws(ws: Worksheet, config: Config) -> dict[str, Any]:
    """
    Lit une feuille de calcul et retourne un dictionnaire contenant
    les informations sur les grilles d'évaluation.
    Se fit aux noms de cellules définis dans la feuille de calcul.
    """
    rubric = config.rubric

    # Récupère le code omnivox
    cell = find_named_cell(ws, CTHM_OMNIVOX)
    if cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_OMNIVOX}' n'existe pas dans la feuille.")
    d = {CTHM_OMNIVOX: cell.value}

    # Récupère le commentaire général
    cell = find_named_cell(ws, CTHM_GLOBAL_COMMENT)
    if cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_GLOBAL_COMMENT}' "
                         "n'existe pas dans la feuille.")
    d[CTHM_GLOBAL_COMMENT] = cell.value

    # Récupère les notes et commentaires
    for criterion in rubric.criteria:
        grade_cell = find_named_cell(ws, criterion.xl_grade_cell_id())
        if grade_cell is None:
            raise ValueError(f"La cellule nommée '{criterion.xl_grade_cell_id()}'"
                             " n'existe pas dans la feuille.")
        grade = round_to_nearest_quantum(Decimal(str(grade_cell.value)), criterion.total_precision)
        d[criterion.xl_grade_cell_id()] = grade

        # Récupère les commentaires
        comment_cell = find_named_cell(ws, criterion.xl_comment_cell_id())
        if comment_cell is None:
            raise ValueError(f"La cellule nommée '{criterion.xl_comment_cell_id()}'"
                             " n'existe pas dans la feuille.")
        comment = "" if comment_cell.value is None else str(comment_cell.value).strip()
        d[criterion.xl_comment_cell_id()] = comment

        for indicator in criterion.indicators:
            # Récupère la note de l'indicateur
            ind_grade_cell = find_named_cell(ws, indicator.xl_grade_cell_id())
            if ind_grade_cell is None:
                raise ValueError(f"La cellule nommée '{indicator.xl_grade_cell_id()}'"
                                 " n'existe pas dans la feuille.")
            ind_grade = Decimal(str(ind_grade_cell.value))
            d[indicator.xl_grade_cell_id()] = ind_grade

            # Récupère le commentaire de l'indicateur
            ind_comment_cell = find_named_cell(ws, indicator.xl_comment_cell_id())
            if ind_comment_cell is None:
                raise ValueError(f"La cellule nommée '{indicator.xl_comment_cell_id()}'"
                                 " n'existe pas dans la feuille.")
            ind_comment = (""  if ind_comment_cell.value is None
                           else str(ind_comment_cell.value).strip())
            d[indicator.xl_comment_cell_id()] = ind_comment

    return d


def generate_feedback(
    config_path: Path | str,
    gradebook_path: Path | str,
    output_dir: Path | str
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’un grille d’évaluation (GradedRubric).
    """
    config_path = Path(config_path)
    gradebook_path = Path(gradebook_path)
    output_dir = Path(output_dir)

    config = Config.from_yaml(config_path)
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config)

    # Génère le document Word
    for grade in grades:
        student = config.find_student(grade[CTHM_OMNIVOX])
        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        title = (student.first_name + " " +
                 student.last_name + " - " +
                 config.evaluation.name + " - " +
                 config.evaluation.course)
        generate_rubric(config.rubric, feedback_path, title=title, grades=grade)

    # Génère le fichier Excel pour charge les notes dans Omnivox
    generate_xl_for_omnivox(config, grades, output_dir)


def generate_xl_for_omnivox(
    config: Config,
    grades: list[dict[str, Any]],
    output_dir: Path | str
) -> None:
    """
    Génère un fichier Excel pour charger les notes dans Omnivox.
    """
    output_dir = Path(output_dir)
    omnivox_path = output_dir / "omnivox.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notes"

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire"])

    # Remplit le tableau avec les notes et les commentaires
    for grade in grades:
        note = sum(grade[criterion.xl_grade_cell_id()] for criterion in config.rubric.criteria)
        comment = grade.get(CTHM_GLOBAL_COMMENT, "")
        ws.append([grade[CTHM_OMNIVOX], note, comment])

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)
