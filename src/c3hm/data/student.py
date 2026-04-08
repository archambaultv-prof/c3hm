import csv
import re
from pathlib import Path

from c3hm.data import JSON_KEY_FIRSTNAME, JSON_KEY_LASTNAME, JSON_KEY_OMNIVOX_ID
from c3hm.data.constants import JSON_KEY_STUDENT_TEAM, JSON_KEY_TEAM_REFERENCE


class Student:
    def __init__(self, omnivox_id: str, firstname: str, surname: str,
                 team: str | None = None, team_reference: bool = False):
        self.omnivox_id = omnivox_id
        self.firstname = firstname
        self.surname = surname
        self.team = team
        self.team_reference = team_reference

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

        if self.team is not None and not self.team.strip():
            raise ValueError("Le nom de l'équipe ne peut pas être vide s'il est fourni.")

        if self.team is None and self.team_reference:
            raise ValueError("Un étudiant ne peut pas être une référence d'équipe s'il n'appartient à aucune équipe.")

    def copy(self) -> "Student":
        return Student(omnivox_id=self.omnivox_id, firstname=self.firstname, surname=self.surname,
                       team=self.team, team_reference=self.team_reference)

    def to_dict(self) -> dict:
        return {
            JSON_KEY_OMNIVOX_ID: self.omnivox_id,
            JSON_KEY_FIRSTNAME: self.firstname,
            JSON_KEY_LASTNAME: self.surname,
            JSON_KEY_STUDENT_TEAM: self.team,
            JSON_KEY_TEAM_REFERENCE: self.team_reference,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        omnivox_id = data.get(JSON_KEY_OMNIVOX_ID, "")
        firstname = data.get(JSON_KEY_FIRSTNAME, "")
        surname = data.get(JSON_KEY_LASTNAME, "")
        team = data.get(JSON_KEY_STUDENT_TEAM)
        team_reference = data.get(JSON_KEY_TEAM_REFERENCE, False)
        return cls(omnivox_id=omnivox_id, firstname=firstname, surname=surname,
                   team=team, team_reference=team_reference)

def read_omnivox_students_file(students_file: Path) -> list[Student]:
    """
    Lit le fichier d'élèves exporté d'Omnivox.
    """
    students = []

    def strip_field(field: str) -> str:
        field = field.strip()
        if field.startswith('="') and field.endswith('"'):
            return field[2:-1]
        return field

    with open(students_file, encoding="ISO-8859-1", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            omnivox_id = row["No de dossier"]
            first_name = row["Prénom de l'étudiant"]
            last_name = row["Nom de l'étudiant"]
            team = row.get("Équipe")
            team_reference = row.get("Référence d'équipe", "").strip().lower()
            team_reference = team_reference in {"oui", "yes", "true", "vrai"}
            student = Student(
                omnivox_id=strip_field(omnivox_id),
                firstname=strip_field(first_name),
                surname=strip_field(last_name),
                team=team,
                team_reference=team_reference
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
