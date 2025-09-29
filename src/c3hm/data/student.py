import csv
from pathlib import Path

from pydantic import BaseModel, Field


class Student(BaseModel):
    omnivox_id: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

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
                first_name=strip_field(first_name),
                last_name=strip_field(last_name)
            )
            students.append(student)
    return students
