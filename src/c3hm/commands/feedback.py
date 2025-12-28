import copy
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.rubric import export_rubric_data
from c3hm.data.rubric import process_single_student_rubric, validate_student
from c3hm.data.student import Student, read_omnivox_students_file


class FeedBackStudent:
    """
    Classe représentant un étudiant pour la génération de rétroaction.
    Contient les informations présentes dans le fichier de rétroaction.
    """
    def __init__(self, name: str, matricule: str, grade: float, comment: str):
        self.name = name
        self.matricule = matricule
        self.grade = grade
        self.comment = comment

def generate_feedback(gradebook_path: Path, output_dir: Path, students_file: Path | None):
    """
    Génère un document Excel de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """

    # Génère le fichier Excel pour charger les notes dans Omnivox
    students = read_omnivox_students_file(students_file) if students_file else None
    students = process_json_files(gradebook_path, output_dir, students)
    generate_xl_for_omnivox(students, output_dir)
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

def process_json_files(
    gradebook_path: Path,
    output_dir: Path | str,
    student_list: list[Student] | None
) -> list[FeedBackStudent]:
    """
    Pour chaque fichier de correction dans le répertoire, génère un fichier PDF
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    json_files = list(gradebook_path.glob("*.json"))
    all_students: list[FeedBackStudent] = []
    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            students: list[dict] = []
            if "étudiant" in data:
                validate_student(data, student_list)
                students.append(data)
            elif "étudiants" in data:
                for s in data["étudiants"]:
                    data2 = copy.deepcopy(data)
                    data2["étudiant"] = copy.deepcopy(s)
                    validate_student(data2, student_list)
                    students.append(data2)
            else:
                raise ValueError("Le fichier JSON doit contenir une section 'étudiant' ou 'étudiants'.")

            if not students:
                print(f"Aucun étudiant trouvé dans le fichier '{json_file}', aucun fichier de rétroaction généré.")
                continue

            for student_data in students:
                name = student_data["étudiant"]["nom"]
                matricule = student_data["étudiant"]["matricule"]
                destination = output_dir / f"{name} {matricule}.pdf"
                data_student = process_single_student_rubric(student_data)
                export_rubric_data(data_student, destination)
                student = FeedBackStudent(
                    name=name,
                    matricule=matricule,
                    grade=data_student["note"],
                    comment=data_student["commentaire"])
                all_students.append(student)
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la génération des fichiers de rétroaction pour le fichier '{json_file}'") from e

    return all_students


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
        omnivox_worksheet.append([student.matricule, student.grade, student.comment, student.name])

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
        showColumnStripes=False
    )
    ws.add_table(table)
