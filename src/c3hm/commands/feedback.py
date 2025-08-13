from pathlib import Path

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.export.export_word import generate_rubric_word
from c3hm.data.config.config import Config
from c3hm.data.gradesheet.gradesheet import GradeSheet
from c3hm.data.gradesheet.gradesheet_parser import grades_from_wb
from c3hm.data.gradesheet.gradesheet_stat import GradeSheetStat


def generate_feedback(
    config: Config,
    gradebook_path: Path | str,
    output_dir: Path | str
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’une feuille de notes.
    """
    gradebook_path = Path(gradebook_path)
    output_dir = Path(output_dir)

    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    students = config.students
    grade_sheets = grades_from_wb(wb, config, students)

    # Génère le document Word
    for grade_sheet in grade_sheets:
        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        student = grade_sheet.student
        feedback_path = output_dir / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        generate_rubric_word(config, feedback_path, grade_sheet)

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
    omnivox_path = output_dir / f"{config.evaluation.name}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is None:
        raise ValueError("Aucune feuille de calcul active trouvée.")
    populate_omnivox_sheet(config, grade_sheets, ws)

    ws = wb.create_sheet()
    populate_averages_sheet(config, grade_sheets, ws)

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)

def populate_omnivox_sheet(config: Config, grade_sheets: list[GradeSheet], ws: Worksheet) -> None:
    ws.title = "Notes pour Omnivox"
    ws.sheet_view.showGridLines = False  # Disable gridlines

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire", "Prénom", "Nom"])

    # Remplit le tableau avec les notes et les commentaires
    for sheet in grade_sheets:
        note = sheet.get_grade(config.evaluation, config.evaluation.points_total_nb_of_decimal)
        comment = None
        if sheet.has_comment(config.evaluation):
            comment = sheet.get_comment(config.evaluation)
        ws.append([sheet.student.omnivox_code, note, comment,
                   sheet.student.first_name, sheet.student.last_name])

    # Format
    _insert_table(ws, "NotesOmnivox", "A1:E" + str(ws.max_row))
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 20


def populate_averages_sheet(config: Config, grade_sheets: list[GradeSheet], ws: Worksheet) -> None:
    stats = GradeSheetStat(grade_sheets)

    ws.title = "Moyennes"
    ws.sheet_view.showGridLines = False  # Disable gridlines

    # Moyenne globale
    ws.append(["Moyenne globale"])
    ws.cell(ws.max_row, 1).style = "Headline 2"
    ws.append(["Évaluation", "Moyenne (pts)", "Moyenne (%)"])
    ws.append(["Évaluation",
               stats.get_grade_average(config.evaluation),
               stats.get_percentage_average(config.evaluation)])
    _insert_table(ws, "MoyenneGlobale", "A2:C3")
    ws.append([])

    # Moyenne par critères
    ws.append(["Moyenne par critères"])
    ws.cell(ws.max_row, 1).style = "Headline 2"
    crit_header_row = ws.max_row + 1
    ws.append(["Critère", "Moyenne (pts)", "Moyenne (%)"])
    crit_count = len(config.evaluation.criteria)
    for criterion in config.evaluation.criteria:
        ws.append([criterion.name,
                   stats.get_grade_average(criterion),
                   stats.get_percentage_average(criterion)])
    # Transforme les données en table
    _insert_table(ws, "MoyenneCriteres", f"A{crit_header_row}:C{crit_header_row + crit_count}")
    ws.append([])

    # Moyenne par indicateurs
    ws.append(["Moyenne par indicateurs"])
    ws.cell(ws.max_row, 1).style = "Headline 2"
    ind_header_row = ws.max_row + 1
    ws.append(["Indicateur", "Moyenne (pts)", "Moyenne (%)", "Critère"])
    ind_count = 0
    for criterion in config.evaluation.criteria:
        ind_count += len(criterion.indicators)
        for indicator in criterion.indicators:
            ws.append([indicator.name,
                       stats.get_grade_average(indicator),
                       stats.get_percentage_average(indicator),
                       criterion.name])
    # Transforme les données en table
    _insert_table(ws, "MoyenneIndicateurs", f"A{ind_header_row}:D{ind_header_row + ind_count}")

    # Applique les formats: pts = 0.0, % = 0.0%
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        # Colonne B (pts)
        if len(row) > 1 and isinstance(row[1].value, int | float):
            row[1].number_format = '0.0'
        # Colonne C (%)
        if len(row) > 2 and isinstance(row[2].value, int | float):
            row[2].number_format = '0.0%'
    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 60


def _insert_table(ws: Worksheet, display_name: str, ref: str) -> None:
    table = Table(displayName=display_name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False
    )
    ws.add_table(table)
