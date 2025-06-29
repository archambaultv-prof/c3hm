from pathlib import Path

import openpyxl as pyxl
from openpyxl.styles import Font, Border, Side
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.data.config import Config
from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.evaluation.indicator import Indicator
from c3hm.data.rubric.rubric import Rubric
from c3hm.data.student.student import Student
from c3hm.utils.excel import (
    CTHM_EVAL_COMMENT,
    CTHM_EVAL_POINTS,
    CTHM_OMNIVOX,
    cell_addr,
    comment_cell_name,
    define_ws_named_cell,
    grade_cell_name,
)


def generate_gradebook(config: Config, output_path: Path | str) -> None:
    """
    Génère un document Excel servant à la correction à partir d’une Rubric
    """
    if not config.students:
        raise ValueError("Aucun étudiant dans la configuration.")

    wb = pyxl.Workbook()
    for sheet in wb.worksheets:
        wb.remove(sheet)

    for student in config.students:
        # Crée une feuille pour chaque étudiant
        ws = wb.create_sheet(title=student.ws_name())
        add_student_sheet(ws, config.rubric, student)

    wb.save(output_path)

def add_student_sheet(ws: Worksheet, rubric: Rubric, student: Student) -> None:
    ws.sheet_view.showGridLines = False

    # Tailles de colonnes
    ws.column_dimensions['A'].width = 50  # Critère ou indicateur
    ws.column_dimensions['B'].width = 10  # Note en %
    ws.column_dimensions['C'].width = 10  # Note en pts
    ws.column_dimensions['D'].width = 70  # Commentaire
    ws.column_dimensions['E'].width = 11  # Note en % calculée
    ws.column_dimensions['F'].width = 11  # Note en pts calculée
    ws.column_dimensions['G'].width = 15  # Niveau calculé

    # Titre
    ws.append([rubric.evaluation.title()])
    ws.cell(row=ws.max_row, column=1).style = "Title"
    ws.append([])

    # Info étudiant + commentaire général
    ws.append(["Étudiant", f"{student.first_name} {student.last_name}"])
    ws.append(["Code omnivox", f"{student.omnivox_code}"])
    define_ws_named_cell(ws, ws.max_row, 2, CTHM_OMNIVOX)
    ws.append([])

    # Note globale
    print_header(ws)
    print_grade_row(ws, rubric.evaluation)
    ws.append([])

    # Note pour critères
    print_header(ws)
    for idx, criterion in enumerate(rubric.evaluation.criteria):
        print_grade_row(ws, criterion)
        if idx > 0:
            set_top_border(ws)
        for indicator in criterion.indicators:
            print_grade_row(ws, indicator)

def set_top_border(ws):
    gray_hex = "BBBBBB"
    top_side = Side(border_style="medium", color=gray_hex)
    for i in range(1, 8):
        cell = ws.cell(row=ws.max_row, column=i)
        cell.border = Border(top=top_side)

def print_grade_row(ws: Worksheet, data: Evaluation | Criterion | Indicator) -> None:
    # Nom
    print_name(ws, data)

    # Note en %
    cell = ws.cell(row=ws.max_row, column=2)
    cell.number_format = "0%"

    # Commentaire
    n = CTHM_EVAL_COMMENT if isinstance(data, Evaluation) else comment_cell_name(data.id)
    define_ws_named_cell(ws, ws.max_row, 4, n)

    # Note calculée en %
    cell = ws.cell(row=ws.max_row, column=5)
    cell.value = f"={cell_addr(ws.max_row, 6)} / {data.points}" # type: ignore
    cell.number_format = "0%"
    if isinstance(data, Evaluation | Criterion):
        cell.font = Font(bold=True)

    # Note calculée en pts
    print_pts_cell(ws, data)

def print_pts_cell(ws, data: Evaluation | Criterion | Indicator):
    # Test pour savoir si les deux cellules de notes sont remplies
    both_cell = (f"AND(NOT(ISBLANK({cell_addr(ws.max_row, 2)})),"
                 f"NOT(ISBLANK({cell_addr(ws.max_row, 3)})))")

    # Pour une évaluation ou un critère, en l'absence de note,
    # on utilise la notes des enfants.
    if isinstance(data, Evaluation):
        children = []
        for c in data.criteria:
            children.append(points_cell_name(c))
        children_str = ", ".join(children)
        alternative = "sum(" + children_str + ")"
    elif isinstance(data, Criterion):
        children = []
        for i in data.indicators:
            children.append(points_cell_name(i))
        children_str = ", ".join(children)
        alternative = "sum(" + children_str + ")"
    else:
        alternative = "NA()"

    # Calcul de la note en points
    note_pts = (f"IF(NOT(ISBLANK({cell_addr(ws.max_row, 2)})),"
                f"{cell_addr(ws.max_row, 2)} * {data.points},"
                f"IF(NOT(ISBLANK({cell_addr(ws.max_row, 3)})),"
                f"{cell_addr(ws.max_row, 3)}, {alternative}))")

    # On assemble le tout
    formula = f"=IF({both_cell}, NA(), {note_pts})"

    cell = ws.cell(row=ws.max_row, column=6)
    cell.value = formula
    n = points_cell_name(data)
    define_ws_named_cell(ws, ws.max_row, 6, n)
    if isinstance(data, Evaluation | Criterion):
        cell.font = Font(bold=True)

def points_cell_name(data: Evaluation | Criterion | Indicator) -> str:
    """
    Retourne le nom de la cellule pour la note en points.
    """
    if isinstance(data, Evaluation):
        return CTHM_EVAL_POINTS
    elif isinstance(data, Criterion | Indicator):
        return grade_cell_name(data.id)
    else:
        raise ValueError(f"Type de ligne inconnu: {type(data)}")

def print_name(ws, data: Evaluation | Criterion | Indicator):
    if isinstance(data, Evaluation):
        pts = "pt" if data.points == 1 else "pts"
        ws.append([f"Total sur {data.points} {pts}"])
        cell = ws.cell(row=ws.max_row, column=1)
        cell.style = "Headline 2"
    elif isinstance(data, Criterion):
        pts = "pt" if data.points == 1 else "pts"
        ws.append([f"{data.name} ({data.points} {pts})"])
        cell = ws.cell(row=ws.max_row, column=1)
        cell.style = "Headline 4"
    elif isinstance(data, Indicator):
        pts = "pt" if data.points == 1 else "pts"
        ws.append([f"{data.name} ({data.points} {pts})"])
        cell = ws.cell(row=ws.max_row, column=1)
        cell.style = "Explanatory Text"
    else:
        raise ValueError(f"Type de ligne inconnu: {type(data)}")

def print_header(ws: Worksheet):
    header = [None, "Note en %", "Note en pts", "Commentaire", "Note en %",
              "Note en pts", "Niveau calculé"]
    ws.append(header)
    for idx in range(2, 5):
        cell = ws.cell(row=ws.max_row, column=idx)
        cell.style = "Headline 4"
    for idx in range(5, 8):
        cell = ws.cell(row=ws.max_row, column=idx)
        cell.style = "Calculation"
