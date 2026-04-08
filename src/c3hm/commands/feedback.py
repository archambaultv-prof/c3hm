import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.rubric import export_rubric
from c3hm.data.rubric import Rubric, validate_teammates


def generate_feedback(gradebook_path: Path, output_dir: Path):
    """
    Génère un document Excel de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """

    # Génère le fichier Excel pour charger les notes dans Omnivox
    rubrics = process_json_files(gradebook_path, output_dir)
    generate_xl_for_omnivox(rubrics, output_dir)
    zip_pdfs(output_dir)


def zip_pdfs(dir: Path) -> None:
    """
    Crée une archive ZIP contenant tous les fichiers PDF dans le répertoire de sortie.
    """
    pattern = "*.pdf"
    pdf_files = dir.glob(pattern)
    with ZipFile(dir / "travaux.zip", "w", compression=ZIP_DEFLATED) as zipf:
        for pdf_file in pdf_files:
            zipf.write(pdf_file, pdf_file.name)


def process_json_files(gradebook_path: Path, output_dir: Path | str) -> list[Rubric]:
    """
    Pour chaque fichier de correction dans le répertoire, génère un fichier PDF
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    json_files = [gradebook_path] if gradebook_path.is_file() else list(gradebook_path.glob("*.json"))
    all_rubrics: list[Rubric] = []
    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            rubric = Rubric.from_dict(data)
            rubric.validate()
            all_rubrics.append(rubric)
        except Exception as e:
            raise RuntimeError(
                f"Erreur lors de la lecture du fichier de rétroaction pour le fichier '{json_file}'"
            ) from e

    validate_teammates(all_rubrics)

    for i, rubric in enumerate(all_rubrics):
        try:
            if rubric.student is None:
                raise ValueError(f"Aucun étudiant associé à la grille de correction dans le fichier '{json_files[i]}'.")
            destination = (
                output_dir / f"{rubric.student.fullname(surname_first=True, include_omnivox=True, separator='_')}.pdf"
            )
            export_rubric(rubric, destination)
        except Exception as e:
            raise RuntimeError(
                f"Erreur lors de la génération du fichier de rétroaction pour le fichier '{json_files[i]}'"
            ) from e

    return all_rubrics


def generate_xl_for_omnivox(rubrics: list[Rubric], output_dir: Path | str) -> None:
    """
    Génère un fichier Excel pour charger les notes dans Omnivox.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    omnivox_path = output_dir / "notes_omnivox.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet()
    populate_omnivox_sheet(rubrics, ws)

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)


def populate_omnivox_sheet(rubrics: list[Rubric], omnivox_worksheet: Worksheet) -> None:
    omnivox_worksheet.title = "Notes pour Omnivox"
    omnivox_worksheet.sheet_view.showGridLines = False  # Disable gridlines

    # En-têtes
    omnivox_worksheet.append(["Code omnivox", "Note", "Commentaire", "Nom"])

    # Trouves tous les fichiers excel
    for rubric in rubrics:
        if rubric.student is None:
            raise ValueError("L'étudiant associé à la grille de correction est manquant.")
        omnivox_worksheet.append(
            [rubric.student.omnivox_id, rubric.final_grade(), rubric.comment, rubric.student.fullname()]
        )

    # Format
    _insert_table(omnivox_worksheet, "NotesOmnivox", "A1:D" + str(omnivox_worksheet.max_row))
    omnivox_worksheet.column_dimensions["A"].width = 20
    omnivox_worksheet.column_dimensions["B"].width = 10
    omnivox_worksheet.column_dimensions["C"].width = 70
    omnivox_worksheet.column_dimensions["D"].width = 40


def _insert_table(ws: Worksheet, display_name: str, ref: str) -> None:
    table = Table(displayName=display_name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    ws.add_table(table)
