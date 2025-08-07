from pathlib import Path
from typing import Self

import polars as pl
from pydantic import BaseModel, model_validator

from c3hm.data.student.student import Student


class Students(BaseModel):
    """
    Classe pour gérer les étudiants.
    """
    students: list[Student]

    @model_validator(mode="after")
    def validate_students(self) -> Self:
        """
        Valide la liste des étudiants.
        """
        # Les alias des étudiants doivent être uniques
        aliases = {student.alias for student in self.students}
        if len(aliases) != len(self.students):
            dup = {}
            for student in self.students:
                if student.alias not in dup:
                    dup[student.alias] = 0
                dup[student.alias] += 1
            duplicates = [k for k, v in dup.items() if v > 1]
            raise ValueError(
                "Les alias des étudiants doivent être uniques. "
                f"Vérifiez la liste des étudiants pour {duplicates}"
            )

        # Toutes les équipes doivent avoir un étudiant référent unique
        teams = {student.team for student in self.students if student.team}
        teams_ref = [student.team for student in self.students
                     if student.team and student.is_team_reference]
        if sorted(teams_ref) != sorted(list(teams)):
            # Find the team references that are not unique
            d = {}
            for x in teams_ref:
                if x not in d:
                    d[x] = 0
                d[x] += 1
            duplicates = [k for k, v in d.items() if v > 1]
            # Find the teams that have no team reference
            no_ref_teams = [team for team in teams if team not in teams_ref]
            bad = duplicates + no_ref_teams
            raise ValueError(
                "Chaque équipe doit avoir un étudiant référent unique. "
                f"Vérifiez la liste des étudiants pour {bad}"
            )
        return self

    def find_student(self, omnivox_code: str) -> Student | None:
        """
        Trouve un étudiant dans la liste à partir de son code omnivox.
        """
        for student in self.students:
            if student.omnivox_code == omnivox_code:
                return student
        return None

    def find_other_team_members(self, student: Student) -> list[Student]:
        """
        Trouve les autres membres de l'équipe d'un étudiant.

        Retourne une liste d'étudiants qui sont dans la même équipe que l'étudiant
        donné, à l'exception de l'étudiant lui-même.
        """
        return [
            s for s in self.students
            if s.team == student.team and s.omnivox_code != student.omnivox_code
        ]

    def list_teams(self) -> list[list[Student]]:
        """
        Retourne une liste de listes d'étudiants, où chaque sous-liste
        représente une équipe d'étudiants. Le premier étudiant de chaque
        sous-liste est l'étudiant référent de l'équipe.
        """
        ls = []
        teams: dict[str, list[Student]] = {}
        for student in self.students:
            if student.team:
                if student.team not in teams:
                    teams[student.team] = []
                teams[student.team].append(student)
            else:
                ls.append([student])
        for members in teams.values():
            # On s'assure que le premier membre est l'étudiant référent
            ref = next((s for s in members if s.is_team_reference), None)
            if ref:
                members.remove(ref)
                ls.append([ref] + members)
            else:
                ls.append(members)
        return ls

    def __iter__(self): # type: ignore
        """
        Permet d'itérer sur les étudiants.
        """
        return iter(self.students)

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        """
        Lit les étudiants à partir d'un fichier CSV ou Excel et retourne une instance de Students.
        """
        return cls(students=read_student(path))

def read_student(path: str | Path) -> list[Student]:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return read_student_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        return read_student_excel(path)
    else:
        raise ValueError(
            f"Le format de fichier {path.suffix} n'est pas supporté. "
            "Utilisez un fichier CSV ou Excel."
        )

_rename_columns_dict = {
    "Prénom": "first_name",
    "Nom": "last_name",
    "Code omnivox": "omnivox_code",
    "Alias": "alias",
    "Équipe": "team",
    "Référence d'équipe": "is_team_reference"
}

def _from_dataframe(df: pl.DataFrame) -> list[Student]:
    """
    Convertit un DataFrame Polars en une liste d'instances de Student.
    """
    students = []
    for row in df.to_dicts():
        students.append(Student(**row))
    return students

def read_student_csv(path: str | Path) -> list[Student]:
    """
    Lit un fichier CSV contenant des informations sur les étudiants et retourne
    une liste d'instances de Student.
    """
    df = pl.read_csv(path, encoding="utf-8")
    df = df.rename(_rename_columns_dict, strict=False)
    return _from_dataframe(df)

def read_student_excel(path: str | Path) -> list[Student]:
    """
    Lit un fichier Excel contenant des informations sur les étudiants et retourne
    une liste de dictionnaires représentant chaque étudiant.
    La structure attendue est la même que pour le fichier CSV.
    """
    df = pl.read_excel(path)
    df = df.rename(_rename_columns_dict, strict=False)
    return _from_dataframe(df)
