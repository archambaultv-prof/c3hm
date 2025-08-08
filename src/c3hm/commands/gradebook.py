from pathlib import Path

import openpyxl as pyxl
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import quote_sheetname
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.data.config.config import Config
from c3hm.data.config.criterion import Criterion
from c3hm.data.config.evaluation import Evaluation
from c3hm.data.config.grade_level import GradeLevel
from c3hm.data.config.indicator import Indicator
from c3hm.data.student.student import Student
from c3hm.utils.excel import (
    CTHM_OMNIVOX,
    cell_addr,
    comment_cell_name,
    define_ws_named_cell,
    grade_cell_name,
)

BORDER_GRAY_HEX = "BBBBBB"
FILL_GRAY_HEX = "F5F5F5"
FILL_RED_HEX = "FF9999"

def generate_gradebook(config: Config, output_path: Path | str) -> None:
    """
    Génère un document Excel servant à la correction à partir d’une Rubric
    """
    students = config.students
    if not students:
        raise ValueError(f"Aucun étudiant dans le fichier {config.students}. ")

    wb = pyxl.Workbook()
    for sheet in wb.worksheets:
        wb.remove(sheet)

    teams_list = students.list_teams()
    teams_list.sort(key=lambda x: x[0].last_name)
    color_tab = any(len(teams) > 1 for teams in teams_list)
    tab_color = ["DDEBF7", "C7E8CA"]
    for i, teams in enumerate(teams_list):
        ref = teams[0]
        ws = wb.create_sheet(title=ref.ws_name())
        add_student_sheet(ws, config, ref, None)
        if color_tab:
            # Colorie l'onglet de l'équipe
            ws.sheet_properties.tabColor = tab_color[i % 2]
        for student in teams[1:]:
            # Crée une feuille pour chaque étudiant
            ws = wb.create_sheet(title=student.ws_name())
            add_student_sheet(ws, config, student, ref)
            if color_tab:
                # Colorie l'onglet de l'équipe
                ws.sheet_properties.tabColor = tab_color[i % 2]

    wb.save(output_path)

def add_student_sheet(ws: Worksheet,
                      config: Config,
                      student: Student,
                      ref_student: Student | None) -> None:
    ws.sheet_view.showGridLines = False

    # Tailles de colonnes
    ws.column_dimensions['A'].width = 50  # Critère ou indicateur
    ws.column_dimensions['B'].width = 10  # Note en %
    ws.column_dimensions['C'].width = 10  # Note en pts
    ws.column_dimensions['D'].width = 60  # Commentaire
    ws.column_dimensions['E'].width = 11  # Note en % calculée
    ws.column_dimensions['F'].width = 11  # Note en pts calculée
    ws.column_dimensions['G'].width = 11  # Niveau calculé
    ws.column_dimensions['H'].width = 60  # Descripteur

    # Titre
    ws.append([config.evaluation.title()])
    ws.cell(row=ws.max_row, column=1).style = "Title"
    ws.append([])

    # Info étudiant + commentaire général
    ws.append(["Étudiant", f"{student.first_name} {student.last_name}"])
    ws.append(["Code omnivox", f"{student.omnivox_code}"])
    define_ws_named_cell(ws, ws.max_row, 2, CTHM_OMNIVOX)
    ws.append([])

    # Note globale
    print_header(ws)
    print_grade_row(ws, config.evaluation, config, ref_student)
    ws.append([])

    # Note pour critères
    print_header(ws, descriptor=True)
    for idx, criterion in enumerate(config.evaluation.criteria):
        print_grade_row(ws, criterion, config)
        if idx > 0:
            set_top_border(ws)
        for indicator in criterion.indicators:
            print_grade_row(ws, indicator, config, ref_student)

def set_top_border(ws):
    top_side = Side(border_style="medium", color=BORDER_GRAY_HEX)
    for i in range(1, 9):
        cell = ws.cell(row=ws.max_row, column=i)
        cell.border = Border(top=top_side)

def print_grade_row(ws: Worksheet,
                    data: Evaluation | Criterion | Indicator,
                    config: Config,
                    ref_student: Student | None = None
                    ) -> None:
    # Nom
    print_name(ws, data)

    # Note en %
    cell = ws.cell(row=ws.max_row, column=2)
    cell.number_format = "0%"

    # Commentaire
    comment_name = comment_cell_name(data.excel_id)
    define_ws_named_cell(ws, ws.max_row, 4, comment_name)
    cell = ws.cell(row=ws.max_row, column=4)
    cell.alignment = Alignment(wrap_text=True)
    if ref_student:
        # Si on a un étudiant de référence, on utilise son commentaire
        # par défaut
        cell.value = f"={quote_sheetname(ref_student.ws_name())}!{comment_name}" # type: ignore

    # Note calculée en %
    cell = ws.cell(row=ws.max_row, column=5)
    cell.value = f"={cell_addr(ws.max_row, 6)} / {data.points}" # type: ignore
    cell.number_format = "0%"
    red_fill = PatternFill(start_color=FILL_RED_HEX, end_color=FILL_RED_HEX, fill_type="solid")
    rule1 = CellIsRule(operator="lessThan",
                      formula=["0."],
                      stopIfTrue=True,
                      fill=red_fill)
    ws.conditional_formatting.add(cell.coordinate, rule1)
    rule2 = CellIsRule(operator="greaterThan",
                      formula=["1."],
                      stopIfTrue=True,
                      fill=red_fill)
    ws.conditional_formatting.add(cell.coordinate, rule2)


    # Note calculée en pts
    print_pts_cell(ws, data, ref_student)

    # Niveau calculé
    print_level_cell(ws, data, config.evaluation.grade_levels)

    # Descripteur calculé
    if isinstance(data, Indicator):
        print_descriptor_cell(ws, data, config)

    # Format pour les lignes calculées
    end = 8 if isinstance(data, Evaluation) else 9
    for idx in range(5, end):
        cell = ws.cell(row=ws.max_row, column=idx)
        cell.fill = PatternFill(start_color=FILL_GRAY_HEX, end_color=FILL_RED_HEX,
                                fill_type="solid")
        if isinstance(data, Evaluation | Criterion):
            cell.font = Font(bold=True)

def print_level_cell(ws: Worksheet,
                     data: Evaluation | Criterion | Indicator,
                     levels: list[GradeLevel]) -> None:
    percent = f"{grade_cell_name(data.excel_id)} / {data.points}"
    ifs = "="
    for level in levels:
        ifs += (f"if({percent} >= {level.minimum / 100},")
        ifs += f'"{level.name}", '
    ifs += '""'  # Niveau par défaut
    for _ in levels:
        ifs += ")"  # Ferme les parenthèses pour chaque niveau
    ws.cell(row=ws.max_row, column=7, value=ifs)

def print_descriptor_cell(ws: Worksheet,
                          indicator: Indicator,
                          config: Config) -> None:
    levels = config.evaluation.grade_levels
    desc = indicator.descriptors
    percent = f"{grade_cell_name(indicator.excel_id)} / {indicator.points}"
    ifs = "="
    for i, level in enumerate(levels):
        ifs += (f"if({percent} >= {level.minimum / 100},")
        ifs += f'"{desc[i]}", '
    ifs += '""'  # Niveau par défaut
    for _ in levels:
        ifs += ")"  # Ferme les parenthèses pour chaque niveau
    ws.cell(row=ws.max_row, column=8, value=ifs)

def print_pts_cell(ws,
                   data: Evaluation | Criterion | Indicator,
                   ref_student: Student | None = None) -> None:
    # Test pour savoir si les deux cellules de notes sont remplies
    both_cell = (f"AND(NOT(ISBLANK({cell_addr(ws.max_row, 2)})),"
                 f"NOT(ISBLANK({cell_addr(ws.max_row, 3)})))")

    # Pour une évaluation ou un critère, en l'absence de note,
    # on utilise la notes des enfants.
    if isinstance(data, Evaluation):
        children = []
        for c in data.criteria:
            children.append(grade_cell_name(c.excel_id))
        children_str = ", ".join(children)
        alternative = "sum(" + children_str + ")"
    elif isinstance(data, Criterion):
        children = []
        for i in data.indicators:
            children.append(grade_cell_name(i.excel_id))
        children_str = ", ".join(children)
        alternative = "sum(" + children_str + ")"
    else:
        if ref_student is not None:
            # Si on a un étudiant de référence, on utilise sa note
            # pour l'indicateur, sinon on utilise NA(). La note
            # de l'étudiant de référence provient d'une autre feuille
            alternative = (f"{quote_sheetname(ref_student.ws_name())}!"
                           f"{grade_cell_name(data.excel_id)}")
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
    n = grade_cell_name(data.excel_id)
    define_ws_named_cell(ws, ws.max_row, 6, n)


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
    cell.alignment = Alignment(wrap_text=True)

def print_header(ws: Worksheet, descriptor: bool = False) -> None:
    header = [None, "Note en %", "Note en pts", "Commentaire", "Note en %",
              "Note en pts", "Niveau"]
    if descriptor:
        header.append("Descripteur")
    ws.append(header)
    for idx in range(2, 5):
        cell = ws.cell(row=ws.max_row, column=idx)
        cell.style = "Headline 4"
    end = 9 if descriptor else 8
    for idx in range(5, end):
        cell = ws.cell(row=ws.max_row, column=idx)
        cell.style = "Calculation"
        # No border for calculated cells
        no_border_side = Side(border_style=None)
        cell.border = Border(left=no_border_side, right=no_border_side,
                             top=no_border_side, bottom=no_border_side)
