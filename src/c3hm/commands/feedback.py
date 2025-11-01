from pathlib import Path

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet


def generate_feedback(gradebook_path: Path, output_dir: Path):
    """
    Génère un document Word de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """

    # Génère le fichier Excel pour charger les notes dans Omnivox
    generate_xl_for_omnivox(gradebook_path, output_dir)


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
        raise ValueError("Aucune feuille de calcul active trouvée.")
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
        xl_wb = openpyxl.load_workbook(xl_file, read_only=True, data_only=True)
        # Check for defined range
        if "cthm_matricule" not in xl_wb.defined_names:
            print(f"Avertissement: Le fichier {xl_file} ne contient pas de "
                  "plage nommée 'cthm_matricule'. Il sera ignoré.")
            continue
        d = {}
        for x in ["cthm_note", "cthm_matricule", "cthm_commentaire", "cthm_nom"]:
            named_range = xl_wb.defined_names[x]
            title, dest = next(named_range.destinations)
            x_ws = xl_wb[title]
            cell = x_ws[dest]
            d[x] = cell.value # type: ignore
        note = d["cthm_note"]
        note = parse_grade(note)
        matricule = d["cthm_matricule"]
        comment = d["cthm_commentaire"]
        nom = d["cthm_nom"]
        ws.append([matricule, note, comment, nom])

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
