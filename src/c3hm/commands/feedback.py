import shutil
from pathlib import Path

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet


def generate_feedback(gradebook_path: Path, output_dir: Path):
    """
    Génère un document Excel de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """

    # Génère le fichier Excel pour charger les notes dans Omnivox
    copy_xl_sheets(gradebook_path, output_dir)
    generate_xl_for_omnivox(gradebook_path, output_dir)


def copy_xl_sheets(
    gradebook_path: Path,
    output_dir: Path | str
) -> None:
    """
    Copie les feuilles Excel de rétroaction dans le répertoire de sortie.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    xl_files = list(gradebook_path.glob("*.xlsx"))
    for xl_file in xl_files:
        xl_wb = openpyxl.load_workbook(xl_file, read_only=True, data_only=True)

        # Check how many students are in the file
        students: list[tuple[str, str]] = []
        for ws in xl_wb.worksheets:
            # Check for defined range
            if "cthm_matricule" not in ws.defined_names:
                continue
            named_range = ws.defined_names["cthm_matricule"]
            _, dest = next(named_range.destinations)
            matricule = ws[dest].value

            named_range = ws.defined_names["cthm_nom"]
            _, dest = next(named_range.destinations)
            nom = ws[dest].value
            students.append((matricule, nom))
        if not students:
            # No students found, skip file
            continue
        elif len(students) == 1:
            # Simply copy the file
            destination = output_dir / f"{students[0][0]} {students[0][1]}.xlsx"
            shutil.copyfile(xl_file, destination)
            continue
        else:
            # Multiple students, create a file per student and remove other
            # students' sheet
            for matricule, nom in students:
                destination = output_dir / f"{matricule} {nom}.xlsx"
                shutil.copyfile(xl_file, destination)
                wb = openpyxl.load_workbook(destination)
                sheets_to_remove = []
                for ws in wb.worksheets:
                    # Check for defined range
                    if "cthm_matricule" not in ws.defined_names:
                        continue
                    named_range = ws.defined_names["cthm_matricule"]
                    _, dest = next(named_range.destinations)
                    cell = ws[dest]
                    if cell.value != matricule:
                        sheets_to_remove.append(ws.title)
                    else:
                        ws.title = str(matricule)
                for sheet_name in sheets_to_remove:
                    std = wb[sheet_name]
                    wb.remove(std)
                wb.active = wb.sheetnames.index(str(matricule))
                wb.save(destination)

def generate_xl_for_omnivox(
    gradebook_path: Path,
    output_dir: Path | str
) -> None:
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
    populate_omnivox_sheet(gradebook_path, ws)

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)

def populate_omnivox_sheet(gradebook_path: Path, ws: Worksheet) -> None:
    ws.title = "Notes pour Omnivox"
    ws.sheet_view.showGridLines = False  # Disable gridlines

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire", "Nom"])

    # Trouves tous les fichiers excel
    xl_files = list(gradebook_path.glob("*.xlsx"))
    for xl_file in xl_files:
        has_grades = False
        xl_wb = openpyxl.load_workbook(xl_file, read_only=True, data_only=True)
        for grade_ws in xl_wb.worksheets:
            # Check for defined range
            if "cthm_matricule" not in grade_ws.defined_names:
                continue
            has_grades = True
            d = {}
            for x in ["cthm_note", "cthm_matricule", "cthm_commentaire", "cthm_nom"]:
                named_range = grade_ws.defined_names[x]
                _, dest = next(named_range.destinations)
                cell = grade_ws[dest]
                d[x] = cell.value # type: ignore
            note = d["cthm_note"]
            note = parse_grade(note)
            matricule = d["cthm_matricule"]
            comment = d["cthm_commentaire"]
            nom = d["cthm_nom"]
            ws.append([matricule, note, comment, nom])
        if not has_grades:
            print(f"Aucune note trouvée dans le fichier {xl_file}, il sera ignoré.")

    # Format
    _insert_table(ws, "NotesOmnivox", "A1:D" + str(ws.max_row))
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 40

def parse_grade(note: str | float | int | None) -> float | None:
    if isinstance(note, float | int | None):
        return note
    elif isinstance(note, str):
        try:
            return float(note)
        except ValueError:
            return float(note.split(" ")[0])
    else:
        raise TypeError(f"Type de note inattendu: {type(note)}")

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
