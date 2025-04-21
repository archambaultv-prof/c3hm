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
    for i in range(2, 10):
        ws.column_dimensions[pyxl_utils.get_column_letter(i)].width = 15

    # Titre
    ws.append([rubric.title()])
    cell = ws.cell(row=ws.max_row, column=1)
    cell.style = "Title"
    ws.append([])

    grid = rubric.grid
    scale_colors = scale_color_schemes(len(grid.scale))

    # En-tête
    ws.append([''] + grid.scale)
    for i in range(2, len(grid.scale) + 2):
        cell = ws.cell(row=ws.max_row, column=i)
        cell.style = "Headline 4"
        if scale_colors:
            color = scale_colors[i - 2]
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")


    for criterion in grid.criteria:
        # Critère
        ws.append([criterion.name])
        cell = ws.cell(row=ws.max_row, column=1)
        cell.style = "Headline 3"
        # Descripteur
        for indicator in criterion.indicators:
            ws.append([indicator.name])
            cell = ws.cell(row=ws.max_row, column=1)
            cell.style = "Explanatory Text"
            for i in range(len(indicator.descriptors)):
                color = "D3D3D3"  # Gris clair
                if scale_colors:
                    color = scale_colors[i]
                col_letter = pyxl_utils.get_column_letter(i + 2)
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
