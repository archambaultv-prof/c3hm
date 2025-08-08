from pathlib import Path

import openpyxl

from c3hm.commands.export.export_word import generate_rubric_word
from c3hm.data.config.config import Config
from c3hm.data.gradesheet.gradesheet import GradeSheet
from c3hm.data.gradesheet.gradesheet_parser import grades_from_wb


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
    for student in students:
        grade_sheet = None
        for s in grade_sheets:
            if s.omnivox_code == student.omnivox_code:
                grade_sheet = s
                break
        if grade_sheet is None:
            raise ValueError(
                f"L'étudiant avec le code Omnivox '{student.omnivox_code}' "
                "n'a pas été trouvé dans le fichier de notes."
            )

        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        generate_rubric_word(config, feedback_path, grade_sheet, student)

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
    ws.title = "Notes" # type: ignore

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire"]) # type: ignore

    # Remplit le tableau avec les notes et les commentaires
    for sheet in grade_sheets:
        note = sheet.get_grade(config.evaluation, config.evaluation.points_total_nb_of_decimal)
        if sheet.has_comment(config.evaluation):
            comment = sheet.get_comment(config.evaluation)
        ws.append([sheet.omnivox_code, note, comment]) # type: ignore

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)
