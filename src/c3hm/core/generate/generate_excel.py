from pathlib import Path

import openpyxl as pyxl

from c3hm.core.rubric import Rubric


def generate_excel_from_rubric(rubric: Rubric, output_path: Path | str) -> None:
    """
    Génère un document Excel servant à la correction à partir d’une Rubric
    """
    wb = pyxl.Workbook()
    ws = wb.active

    # Titre
    ws.append([rubric.title()])
    ws.append([])

    grid = rubric.grid
    # En-tête
    ws.append([''] + grid.scale)

    for criterion in grid.criteria:
        # Critère
        ws.append([criterion.name])
        # Descripteur
        for indicator in criterion.indicators:
            ws.append([indicator.name])

    wb.save(output_path)
