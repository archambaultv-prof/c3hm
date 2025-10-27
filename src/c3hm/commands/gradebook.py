import shutil
from pathlib import Path

import openpyxl

from c3hm.data.student import read_omnivox_students_file


def generate_gradebook(rubric: Path, students_file: Path, output_dir: Path) -> None:
    """
    Génère les grilles de correction à partir du fichier de configuration.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")

    students = read_omnivox_students_file(students_file)
    for student in students:
        stem = f"{student.omnivox_id} {student.first_name} {student.last_name}.xlsx"
        destination = output_dir / stem
        shutil.copyfile(rubric, destination)

        # Open file and fill in student info
        wb = openpyxl.load_workbook(destination)

        for name, value in [("cthm_matricule", int(student.omnivox_id)),
                            ("cthm_nom", f"{student.first_name} {student.last_name}")]:
            named_range = wb.defined_names[name]
            for title, dest in named_range.destinations:
                ws = wb[title]
                cell = ws[dest]
                cell.value = value # type: ignore

        wb.save(destination)
