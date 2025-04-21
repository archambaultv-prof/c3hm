from pathlib import Path

import openpyxl as pyxl
import openpyxl.utils as pyxl_utils
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import PatternFill

from c3hm.core.generate.generate_word import scale_color_schemes
from c3hm.core.rubric import Rubric


def generate_excel_from_rubric(rubric: Rubric, output_path: Path | str) -> None:
    """
    Génère un document Excel servant à la correction à partir d’une Rubric
    """
    wb = pyxl.Workbook()
    ws = wb.active
    ws.sheet_view.showGridLines = False

    # Tailles de colonnes
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 6
    for i in range(3, 11):
        ws.column_dimensions[pyxl_utils.get_column_letter(i)].width = 15
    ws.column_dimensions[pyxl_utils.get_column_letter(11)].width = 60

    # Titre
    ws.append([rubric.title()])
    cell = ws.cell(row=ws.max_row, column=1)
    cell.style = "Title"
    ws.append([])

    # Total sur X pts
    pts = "pt" if rubric.grid.total_score == 1 else "pts"
    ws.append([f"Total sur {rubric.grid.total_score} {pts}"])
    cell = ws.cell(row=ws.max_row, column=1)
    cell.style = "Headline 2"

    cell = ws.cell(row=ws.max_row, column=2)
    cell.style = "Calculation"

    # Grille
    grid = rubric.grid
    scale_colors = scale_color_schemes(len(grid.scale))

    # En-tête - seuils
    col_before_scale = 2
    ws.append([''] * col_before_scale + grid.thresholds)
    for i in range(col_before_scale + 1, len(grid.thresholds) + col_before_scale + 1):
        cell = ws.cell(row=ws.max_row, column=i)
        cell.style = "Explanatory Text"

    # En-tête - barème
    extra_cols = ["note calculée", "note manuelle", "note en pts", "commentaires"]
    ws.append([''] * col_before_scale + grid.scale + extra_cols)
    for i in range(col_before_scale + 1, len(grid.scale) + col_before_scale + 1 + len(extra_cols)):
        cell = ws.cell(row=ws.max_row, column=i)
        cell.style = "Headline 4"
        if scale_colors and i - col_before_scale - 1 < len(scale_colors):
            color = scale_colors[i - col_before_scale - 1]
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")


    for criterion in grid.criteria:
        # Critère
        ws.append([criterion.name, criterion.weight])
        cell = ws.cell(row=ws.max_row, column=1)
        cell.style = "Headline 3"

        cell = ws.cell(row=ws.max_row, column= col_before_scale + len(grid.scale) + 1)
        cell.style = "Calculation"

        cell = ws.cell(row=ws.max_row, column= col_before_scale + len(grid.scale) + 2)
        cell.style = "Input"

        cell = ws.cell(row=ws.max_row, column= col_before_scale + len(grid.scale) + 3)
        cell.style = "Calculation"

        # Descripteur
        for indicator in criterion.indicators:
            ws.append([indicator.name, 1])
            for i in range(2):
                cell = ws.cell(row=ws.max_row, column=i+2)
                cell.style = "Explanatory Text"
            for i in range(len(indicator.descriptors)):
                color = "D3D3D3"  # Gris clair
                if scale_colors:
                    color = scale_colors[i]
                col_letter = pyxl_utils.get_column_letter(i + col_before_scale + 1)
                rule = FormulaRule(
                    formula=[f'NOT(ISBLANK({col_letter}{ws.max_row}))'],
                    stopIfTrue=True,
                    fill=PatternFill(start_color=color, end_color=color, fill_type="solid")
                )
                ws.conditional_formatting.add(
                    f'{col_letter}{ws.max_row}',
                    rule
                )

    wb.save(output_path)
