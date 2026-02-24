import json
from pathlib import Path

from c3hm.data.rubric import Rubric
from c3hm.data.student import Student, read_omnivox_students_file


def generate_gradebook(rubric: Path, output_dir: Path, students_file: Path | None) -> None:
    """
    Génère les grilles de correction à partir du fichier de configuration.
    """
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    with open(rubric, encoding="utf-8") as f:
        rubric_data = json.load(f)
    r = Rubric.from_dict(rubric_data)
    r.validate()

    if students_file:
        generate_gradebook_from_students_file(r, students_file, output_dir)
    else:
        new_rubric = r.copy()
        student = Student(omnivox_id="", firstname="", surname="")
        new_rubric.student = student
        output_path = output_dir / "grille de correction.json"
        write_gradebook(new_rubric, output_path)


def generate_gradebook_from_students_file(rubric: Rubric, students_file: Path, output_dir: Path) -> None:
    students = read_omnivox_students_file(students_file)
    for student in students:
        student.validate()
        new_rubric = rubric.copy()
        new_rubric.student = student
        stem = f"{student.fullname(surname_first=True, include_omnivox=True, separator='_')}.json"
        destination = output_dir / stem
        write_gradebook(new_rubric, destination)


def write_gradebook(rubric: Rubric, output_path: Path) -> None:
    rubric_dict = rubric.to_dict()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rubric_dict, f, ensure_ascii=False, indent=4)
