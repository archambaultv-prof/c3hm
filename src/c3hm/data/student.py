import csv
import re
from pathlib import Path


class Student:
    def __init__(self, omnivox_id: str, name: str):
        self.omnivox_id = omnivox_id
        self.name = name

    def validate(self) -> None:
        if not self.omnivox_id.strip():
            raise ValueError("L'identifiant Omnivox ne peut pas être vide.")

        if not self.name.strip():
            raise ValueError("Le nom de l'étudiant ne peut pas être vide.")

    def copy(self) -> 'Student':
        return Student(omnivox_id=self.omnivox_id, name=self.name)

def read_omnivox_students_file(students_file: Path) -> list[Student]:
    """
    Lit le fichier d'élèves exporté d'Omnivox.
    """
    students = []
    def strip_field(field: str) -> str:
        return field[2:-1]

    with open(students_file, encoding="ISO-8859-1", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            omnivox_id = row["No de dossier"]
            first_name = row["Prénom de l'étudiant"]
            last_name = row["Nom de l'étudiant"]
            student = Student(
                omnivox_id=strip_field(omnivox_id),
                name=strip_field(first_name) + " " + strip_field(last_name),
            )
            students.append(student)
    return students

def find_student_by_name(name: str, student_list: list[Student]) -> Student:
    """
    Trouve un étudiant dans la liste par son nom ou une partie de son nom.
    Le nom peut contenir plusieurs parties (prénom et/ou nom).
    """
    names = [x.strip().lower() for x in re.split(r"[\s-]+", name)]
    found = []
    for student in student_list:
        names = [x.strip().lower() for x in re.split(r"[\s-]+", student.name)]
        match = True
        for n in names:
            if n not in names:
                match = False
                break
        if match:
            found.append(student)
    if len(found) == 1:
        return found[0]
    elif len(found) > 1:
        raise ValueError(f"Multiple students found for name '{name}'")
    else:
        raise ValueError(f"No student found for name '{name}'")
