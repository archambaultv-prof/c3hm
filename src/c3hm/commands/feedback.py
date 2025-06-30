from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.export.generate_rubric import generate_rubric
from c3hm.data.config import Config
from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.evaluation.indicator import Indicator
from c3hm.data.gradesheet import GradeSheet
from c3hm.utils.excel import (
    CTHM_OMNIVOX,
    comment_cell_name,
    grade_cell_name,
)


def grades_from_wb(
    wb: Workbook,
    config: Config,
) -> list[GradeSheet]:
    """
    Lit le fichier Excel et retourne une liste d'évaluations notées
    """
    grade_sheets = []

    for student in config.students:
        ws = find_worksheet(wb, student.alias)
        grade_sheets.append(grades_from_ws(ws, config.rubric.evaluation))
    return grade_sheets

def find_worksheet(wb: Workbook, alias: str) -> Worksheet:
    """
    Trouve la feuille de calcul correspondant à l'alias de l'étudiant.
    Si la feuille n'existe pas, lève une erreur.
    """
    for ws in wb.worksheets:
        if ws.title == alias:
            return ws
    raise ValueError(f"La feuille de calcul pour l'alias '{alias}' n'existe pas.")

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
            try:
                cell = ws[coord]
            except IndexError as e:
                print(f"Erreur lors de la récupération de la cellule '{named_cell}'")
                print(f"Feuille : {ws.title}")
                raise e
            return cell

    return None


def grades_from_ws(ws: Worksheet,
                   eval: Evaluation) -> GradeSheet:
    """
    Lit une feuille de calcul et retourne une évaluation notée.
    Se fit aux noms de cellules définis dans la feuille de calcul.
    """

    omnivox_code = str(get_cell_value(ws, CTHM_OMNIVOX))
    comments = {}
    grades = {}

    collect_comment_grade(ws, eval, comments, grades)
    for c in eval.criteria:
        collect_comment_grade(ws, c, comments, grades)
        for i in c.indicators:
            collect_comment_grade(ws, i, comments, grades)

    return GradeSheet(
        omnivox_code=omnivox_code,
        comments=comments,
        grades=grades,
    )

def collect_comment_grade(ws: Worksheet,
                      x : Evaluation | Criterion | Indicator,
                      comments: dict[str, str],
                      grades: dict[str, float]) -> None:
    c = get_cell_value(ws, comment_cell_name(x.id), allow_none=True)
    if c and str(c).strip():
        comments[x.id] = str(c).strip()
    grades[x.id] = float(get_cell_value(ws, grade_cell_name(x.id))) # type: ignore

def get_cell_value(ws: Worksheet,
                   name: str,
                   allow_none: bool = False):
    cell = find_named_cell(ws, name)
    if cell is None:
        raise ValueError(f"La cellule nommée '{name}'"
                            " n'existe pas dans la feuille.")
    if cell.value is None:
        if allow_none:
            return None
        else:
            raise ValueError(f"La cellule nommée '{name}' ne peut pas être vide.")
    if str(cell.value).strip().upper() == "#N/A":
        raise ValueError(f"La cellule nommée '{name}' ne peut pas contenir '#N/A'.")
    return cell.value


def generate_feedback(
    config_path: Path | str,
    gradebook_path: Path | str,
    output_dir: Path | str
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’une feuille de notes.
    """
    config_path = Path(config_path)
    gradebook_path = Path(gradebook_path)
    output_dir = Path(output_dir)

    config = Config.from_user_config(config_path)
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grade_sheets = grades_from_wb(wb, config)

    # Génère le document Word
    for student in config.students:
        grade_sheet = None
        for s in grade_sheets:
            if s.omnivox_code == student.omnivox_code:
                grade_sheet = s
                break
        if grade_sheet is None:
            raise ValueError(
                f"L'étudiant avec le code Omnivox '{student.omnivox_code}' "
                "n'a pas été trouvé dans le fichier de notes."
            )

        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        generate_rubric(config.rubric, feedback_path, grade_sheet, student)

    # Génère le fichier Excel pour charger les notes dans Omnivox
    generate_xl_for_omnivox(config, grade_sheets, output_dir)


def generate_xl_for_omnivox(
    config: Config,
    grade_sheets: list[GradeSheet],
    output_dir: Path | str
) -> None:
    """
    Génère un fichier Excel pour charger les notes dans Omnivox.
    """
    output_dir = Path(output_dir)
    omnivox_path = output_dir / f"{config.rubric.evaluation.name}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notes" # type: ignore

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire"]) # type: ignore

    # Remplit le tableau avec les notes et les commentaires
    for sheet in grade_sheets:
        note = sheet.get_grade(config.rubric.evaluation, config.rubric.evaluation.precision)
        comment = sheet.get_comment(config.rubric.evaluation)
        ws.append([sheet.omnivox_code, note, comment]) # type: ignore

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)
