import shutil
from pathlib import Path

import openpyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.data.student import Student, find_student_by_name, read_omnivox_students_file


class FeedBackStudent:
    """
    Classe représentant un étudiant pour la génération de rétroaction.
    Contient les informations présentes dans le fichier de rétroaction.
    """
    def __init__(self, student: Student, sheet_name: str,
                 grade: float | str | int, comment: str):
        self.student = student
        self.sheet_name = sheet_name
        self.grade = parse_grade(grade)
        self.comment = comment

def generate_feedback(gradebook_path: Path, output_dir: Path, students_file: Path):
    """
    Génère un document Excel de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """

    # Génère le fichier Excel pour charger les notes dans Omnivox
    students = read_omnivox_students_file(students_file)
    students = copy_xl_sheets(gradebook_path, output_dir, students)
    generate_xl_for_omnivox(students, output_dir)


def copy_xl_sheets(
    gradebook_path: Path,
    output_dir: Path | str,
    student_list: list[Student]
) -> list[FeedBackStudent]:
    """
    Copie les feuilles Excel de rétroaction dans le répertoire de sortie.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    xl_files = list(gradebook_path.glob("*.xlsx"))
    all_students: list[FeedBackStudent] = []
    for xl_file in xl_files:
        try:
            xl_wb = openpyxl.load_workbook(xl_file, read_only=True, data_only=True)

            # Check how many students are in the file
            students = extract_students_from_workbook(student_list, xl_file, xl_wb)

            if not students:
                print(f"Aucun étudiant trouvé dans le fichier '{xl_file}', on passe au suivant.")
                continue

            # Multiple students, create a file per student and remove other
            # students' sheet
            for student in students:
                destination = output_dir / f"{student.student.omnivox_id} {student.student.full_name()}.xlsx"
                shutil.copyfile(xl_file, destination)
                wb = openpyxl.load_workbook(destination)

                filter_student_sheets(student, wb)
                update_omnivox_id_in_workbook(student, wb)

                wb.save(destination)

        except Exception as e:
            raise RuntimeError(f"Erreur lors de la génération des fichiers de rétroaction pour le fichier '{xl_file}'") from e

        all_students.extend(students)
    return all_students

def filter_student_sheets(student: FeedBackStudent, wb: Workbook) -> None:
    sheets_to_remove = []
    for ws in wb.worksheets:
        # On garde les feuilles qui ne contiennent pas de rétroaction pour un étudiant
        # (ex: feuille d'équipe)
        if "cthm_nom" not in ws.defined_names:
            continue

        # On garde bien sûr la feuille de l'étudiant
        if ws.title == student.sheet_name:
            continue

        sheets_to_remove.append(ws.title)

    for sheet_name in sheets_to_remove:
        std = wb[sheet_name]
        wb.remove(std)

def extract_students_from_workbook(student_list: list[Student], xl_file: Path, xl_wb: Workbook) -> list[FeedBackStudent]:
    students: list[FeedBackStudent] = []
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

        named_range = ws.defined_names["cthm_note"]
        _, dest = next(named_range.destinations)
        note = ws[dest].value

        named_range = ws.defined_names["cthm_commentaire"]
        _, dest = next(named_range.destinations)
        comment = ws[dest].value

        if matricule is None and nom is None:
            continue  # Feuille non utilisée


        student = find_student_by_name(nom, student_list)
        matricule = student.omnivox_id
        students.append(FeedBackStudent(student=student, sheet_name=ws.title, grade=note,
                                        comment=comment))

    return students

def update_omnivox_id_in_workbook(student: FeedBackStudent, wb: Workbook) -> None:
    nb_found = 0
    for ws in wb.worksheets:
                    # Check for defined range
        if "cthm_matricule" not in ws.defined_names:
            continue

        # Double check that only one sheet has cthm_matricule
        nb_found += 1
        if nb_found > 1:
            raise ValueError(f"Multiple sheets with 'cthm_matricule' found in workbook '{student.student.full_name()}'")

        named_range = ws.defined_names["cthm_matricule"]
        _, dest = next(named_range.destinations)
        cell = ws[dest]
        cell.value = student.student.omnivox_id

        named_range = ws.defined_names["cthm_nom"]
        _, dest = next(named_range.destinations)
        cell = ws[dest]
        cell.value = student.student.full_name()

def generate_xl_for_omnivox(
    students: list[FeedBackStudent],
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
    populate_omnivox_sheet(students, ws)

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)

def populate_omnivox_sheet(students: list[FeedBackStudent], omnivox_worksheet: Worksheet) -> None:
    omnivox_worksheet.title = "Notes pour Omnivox"
    omnivox_worksheet.sheet_view.showGridLines = False  # Disable gridlines

    # En-têtes
    omnivox_worksheet.append(["Code omnivox", "Note", "Commentaire", "Nom"])

    # Trouves tous les fichiers excel
    for student in students:
        omnivox_worksheet.append([student.student.omnivox_id, student.grade, student.comment, student.student.full_name()])

    # Format
    _insert_table(omnivox_worksheet, "NotesOmnivox", "A1:D" + str(omnivox_worksheet.max_row))
    omnivox_worksheet.column_dimensions["A"].width = 20
    omnivox_worksheet.column_dimensions["B"].width = 10
    omnivox_worksheet.column_dimensions["C"].width = 70
    omnivox_worksheet.column_dimensions["D"].width = 40

def parse_grade(note: str | float | int | None) -> float | None:
    if note is None:
        raise ValueError("La note ne peut pas être None")
    if isinstance(note, float | int | None):
        return note
    elif isinstance(note, str):
        note = note.strip().split(" ")[0].strip().replace(",", ".")
        return float(note)
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
