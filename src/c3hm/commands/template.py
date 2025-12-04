from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.styles import Alignment, PatternFill
from openpyxl.utils import absolute_coordinate, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName

DEFAULT_GRID_SIZE = 4  # Nombre par défaut de critères et d'indicateurs

PERFECT_GREEN    = "C8FFC8"  # RGB(200, 255, 200)
VERY_GOOD_GREEN  = "F0FFB0"  # RGB(240, 255, 176)
HALF_WAY_YELLOW  = "FFF8C2"  # RGB(255, 248, 194)
MINIMAL_RED      = "FFE4C8"  # RGB(255, 228, 200)
BAD_RED          = "FFC8C8"  # RGB(255, 200, 200)

GRADE_COLORS = {
    2: [PERFECT_GREEN, BAD_RED],
    3: [PERFECT_GREEN, HALF_WAY_YELLOW, BAD_RED],
    4: [PERFECT_GREEN, VERY_GOOD_GREEN, HALF_WAY_YELLOW, BAD_RED],
    5: [PERFECT_GREEN, VERY_GOOD_GREEN, HALF_WAY_YELLOW, MINIMAL_RED, BAD_RED],
}

GRADE_LEVELS = {
    2: ["Réussi", "Insuffisant"],
    3: ["Très bien", "Acceptable", "Insuffisant"],
    4: ["Très bien", "Bien", "Passable", "Insuffisant"],
    5: ["Excellent", "Très bien", "Bien", "Passable", "Insuffisant"],
}

GRADE_PERCENTAGES = {
    2: [1.0, 0],
    3: [1.0, 0.6, 0],
    4: [1.0, 0.8, 0.6, 0],
    5: [1.0, 0.9, 0.75, 0.6, 0],
}

def distribute_points(total_points: int, num_items: int) -> list[int]:
    """
    Distribue un nombre total de points équitablement entre un nombre d'items.
    Les valeurs ne diffèrent pas de plus de 1.
    """
    base_value = total_points // num_items
    remainder = total_points % num_items

    # Les 'remainder' premiers items reçoivent base_value + 1, les autres base_value
    points = [base_value + 1 if i < remainder else base_value for i in range(num_items)]

    return points


def export_template(output_path: Path,
                    nb_levels: int = 4,
                    criteria_indicators: list[int] | None = None) -> None:
    """
    Génère une grille d'évaluation sous format Excel.
    """
    if nb_levels < 2 or nb_levels > 5:
        raise ValueError("Le nombre de niveaux doit être entre 2 et 5.")

    if criteria_indicators is None:
        criteria_indicators = [DEFAULT_GRID_SIZE] * DEFAULT_GRID_SIZE

    if not criteria_indicators:
        raise ValueError("Il faut au moins un critère.")

    if any(n < 1 for n in criteria_indicators):
        raise ValueError("Chaque critère doit avoir au moins un indicateur.")

    nb_criteria = len(criteria_indicators)
    total_indicators = sum(criteria_indicators)
    indicator_points = distribute_points(100, total_indicators)

    grade_col = 4 + nb_levels
    grade_letter = chr(ord("D") + nb_levels).upper()
    comment_col = grade_col + 1

    # Create new workbook
    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise RuntimeError("Impossible de créer la feuille de calcul.")
    ws.title = "Grille"
    ws.sheet_view.showGridLines = False

    def create_defined_name(name, cell_coord):
        ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell_coord)}"
        defn = DefinedName(name, attr_text=ref)
        wb.defined_names[name] = defn

    # Set column widths
    ws.column_dimensions["A"].width = 2.5
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 13
    for i in range(nb_levels):
        col_letter = chr(ord("D") + i)
        ws.column_dimensions[col_letter].width = 17
    ws.column_dimensions[chr(ord("D") + nb_levels)].width = 12  # Grade column
    ws.column_dimensions[chr(ord("D") + nb_levels + 1)].width = 70  # Comment column

    # Create header
    ws.cell(row=2, column=2, value="Matricule")
    create_defined_name("cthm_matricule", "C2")

    set_header_style(ws.cell(row=2, column=2)) # type: ignore
    ws.cell(row=2, column=4, value="Nom")
    create_defined_name("cthm_nom", "E2")

    set_header_style(ws.cell(row=2, column=4)) # type: ignore
    ws.cell(row=3, column=2, value="Note")
    create_defined_name("cthm_note", "C3")
    ws.cell(row=3, column=3,
            value=f'=_xlfn.CONCAT(SUM({all_indicators_range(grade_letter, criteria_indicators)})," points")')

    set_header_style(ws.cell(row=3, column=2)) # type: ignore
    ws.cell(row=3, column=4, value="Commentaire")
    create_defined_name("cthm_commentaire", "E3")

    set_header_style(ws.cell(row=3, column=4)) # type: ignore
    ws.cell(row=5, column=2, value="Session")
    set_header_style(ws.cell(row=5, column=2)) # type: ignore
    ws.cell(row=5, column=3, value=f"{get_current_session()}")
    ws.cell(row=5, column=4, value="Cours")
    set_header_style(ws.cell(row=5, column=4)) # type: ignore

    ws.cell(row=5, column=6, value="Évaluation")
    set_header_style(ws.cell(row=5, column=6)) # type: ignore


    # Create grid

    ws.cell(row=8, column=3,
            value=f'=_xlfn.CONCAT("Total sur ",SUM({all_indicators_range("C", criteria_indicators, include_penalty=False)})," points")')
    ws.cell(row=8, column=3).style = "Explanatory Text"
    for criterion_idx in range(nb_criteria):
        # Déterminer la ligne du critère
        nb_indicators = criteria_indicators[criterion_idx]
        criterion_row = 9 + sum(criteria_indicators[:criterion_idx]) + criterion_idx
        ws.cell(row=criterion_row, column=2,
                value=f"Critère {criterion_idx + 1}")
        ws.cell(row=criterion_row, column=2).style = "Headline 1"

        pts_range = f"C{criterion_row + 1}:C{criterion_row + nb_indicators}"
        ws.cell(row=criterion_row, column=3, value=f'=_xlfn.CONCAT(SUM({pts_range})," points")')
        ws.cell(row=criterion_row, column=3).style = "Explanatory Text"

        for level_idx in range(nb_levels):
            perc = int(GRADE_PERCENTAGES[nb_levels][level_idx] * 100)
            if perc == 0:
                perc = f"< {int(GRADE_PERCENTAGES[nb_levels][level_idx - 1] * 100)}"
            elif perc < 100:
                perc = f"≥ {perc}"
            ws.cell(row=criterion_row,
                    column=4 + level_idx,
                    value=f"{GRADE_LEVELS[nb_levels][level_idx]} ({perc}%)")
            color = GRADE_COLORS[nb_levels][level_idx]
            cell = ws.cell(row=criterion_row, column=4 + level_idx)
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        pts_range = f"{grade_letter}{criterion_row + 1}:{grade_letter}{criterion_row + nb_indicators}"
        ws.cell(row=criterion_row, column=grade_col,
                value=f'=_xlfn.CONCAT("Note : ",SUM({pts_range}))')

        ws.cell(row=criterion_row, column=comment_col, value="Commentaire")

        # Create indicators
        for indicator_idx in range(nb_indicators):
            indicator_row = criterion_row + indicator_idx + 1
            # Calculer l'index global de l'indicateur
            global_indicator_idx = sum(criteria_indicators[:criterion_idx]) + indicator_idx

            ws.cell(row=indicator_row, column=2,
                    value=f"Indicateur {criterion_idx + 1}.{indicator_idx + 1}")
            ws.cell(row=indicator_row, column=3, value=indicator_points[global_indicator_idx])
            ws.cell(row=indicator_row, column=3).style = "Explanatory Text"

            # Centrer les cellules de niveau de performance
            for level_idx in range(nb_levels):
                cell = ws.cell(row=indicator_row, column=4 + level_idx)
                cell.alignment = Alignment(horizontal="center")

            # Insert grade formula
            xs = []
            for level_idx in range(nb_levels):
                cell_letter = chr(ord("D") + level_idx)
                cell_coord = f"{cell_letter}{indicator_row}"
                default_percent = GRADE_PERCENTAGES[nb_levels][level_idx]
                grade_or_percent = (f'IF(LEFT(_xlfn.CELL("format", {cell_coord}),1)="P",'
                                    f'C{indicator_row}*{cell_coord},{cell_coord})')
                xs.append(f"IF(ISTEXT({cell_coord}),C{indicator_row}*{default_percent},{grade_or_percent})")
            counta_range = f"D{indicator_row}:{chr(ord('D') + nb_levels - 1)}{indicator_row}"
            formula = f"=IF(COUNTA({counta_range})>1,NA()," + "+".join(xs) + ")"
            ws.cell(row=indicator_row, column=grade_col, value = formula)

    # Pénalités pour retard, français, fautes significatives
    total_indicators = sum(criteria_indicators)
    penalty_row = 9 + total_indicators + nb_criteria + 1
    ws.cell(row=penalty_row, column=3 + nb_levels + 1, value="Points")
    ws.cell(row=penalty_row, column=3 + nb_levels + 2, value="Commentaire")

    ws.cell(row=penalty_row + 1, column=2, value="Bonus / Malus")
    ws.cell(row=penalty_row + 1, column=2).style = "Headline 1"
    ws.cell(row=penalty_row + 1, column=3 + nb_levels + 1, value=0)

    ws.cell(row=penalty_row + 2, column=2,
            value="En plus de la grille ci-dessus, il est possible "
                  "que des points soient retirés pour :")
    ws.cell(row=penalty_row + 3, column=2, value="- un retard")
    ws.cell(row=penalty_row + 4, column=2, value="- des fautes de français")
    ws.cell(row=penalty_row + 5, column=2,
            value="- une erreur significative (non respect "
                  "des conventions d'usage, absence de commentaires lorsque nécessaire, "
                  "code spaghetti, code qui plante ou ne démarre pas, etc.)")
    for i in range(4):
        ws.cell(row=penalty_row + 2 + i, column=2).style = "Explanatory Text"


    # Save workbook
    wb.save(output_path)

def get_current_session() -> str:
    today = date.today()
    year = today.year
    if today.month <= 5:
        return f"Hiver {year}"
    elif today.month <= 7:
        return f"Été {year}"
    else:
        return f"Automne {year}"

def set_header_style(cell: Cell):
    cell.style = "Headline 4"
    cell.alignment = Alignment(horizontal="right")

def all_indicators_range(col_letter: str, criteria_indicators: list[int],
                         include_penalty: bool = True) -> str:
    r = []
    for criterion_idx, nb_indicators in enumerate(criteria_indicators):
        row_start = 10 + sum(criteria_indicators[:criterion_idx]) + criterion_idx
        row_end = row_start + nb_indicators - 1
        r.append(f"{col_letter}{row_start}:{col_letter}{row_end}")
    total_indicators = sum(criteria_indicators)
    if include_penalty:
        nb_criteria = len(criteria_indicators)
        penalty_row = 9 + total_indicators + nb_criteria + 2
        r.append(f"{col_letter}{penalty_row}")
    return ",".join(r)
