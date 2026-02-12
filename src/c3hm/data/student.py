import csv
import re
from pathlib import Path


class Student:
    def __init__(self, omnivox_id: str, firstname: str, surname: str):
        self.omnivox_id = omnivox_id
        self.firstname = firstname
        self.surname = surname

    def fullname(
        self,
        surname_first: bool = False,
        include_omnivox: bool = False,
        separator: str = " ",
    ) -> str:
        parts = [self.surname, self.firstname] if surname_first else [self.firstname, self.surname]
        name = separator.join(part.strip() for part in parts)
        if include_omnivox:
                return f"{name}{separator}{self.omnivox_id.strip()}"
        return name

    def validate(self) -> None:
        if not self.omnivox_id.strip():
            raise ValueError("L'identifiant Omnivox ne peut pas être vide.")

        if not self.firstname.strip():
            raise ValueError("Le prénom de l'étudiant ne peut pas être vide.")

        if not self.surname.strip():
            raise ValueError("Le nom de famille de l'étudiant ne peut pas être vide.")

    def copy(self) -> 'Student':
        return Student(omnivox_id=self.omnivox_id, firstname=self.firstname, surname=self.surname)

    def to_dict(self) -> dict:
        return {
            "matricule": self.omnivox_id,
            "prénom": self.firstname,
            "nom": self.surname
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        omnivox_id = data.get("matricule", "")
        firstname = data.get("prénom", "")
        surname = data.get("nom", "")
        return cls(omnivox_id=omnivox_id, firstname=firstname, surname=surname)

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
                firstname=strip_field(first_name),
                surname=strip_field(last_name),
            )
            students.append(student)
    return students

def find_student_by_name(name: str, student_list: list[Student]) -> Student:
    """
    Trouve un étudiant dans la liste par son nom ou une partie de son nom.
    Le nom peut contenir plusieurs parties (prénom et/ou nom).
    """
    query_parts = [x.strip().lower() for x in re.split(r"[\s-]+", name) if x.strip()]
    found = []
    for student in student_list:
        student_parts = [x.strip().lower() for x in re.split(r"[\s-]+", student.fullname()) if x.strip()]
        if all(part in student_parts for part in query_parts):
            found.append(student)
    if len(found) == 1:
        return found[0]
    elif len(found) > 1:
        raise ValueError(f"Multiple students found for name '{name}'")
    else:
        raise ValueError(f"No student found for name '{name}'")
