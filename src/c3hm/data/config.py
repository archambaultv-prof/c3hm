from pathlib import Path

import yaml
from pydantic import BaseModel

from c3hm.data.rubric.rubric import Rubric
from c3hm.data.student.student import Student
from c3hm.data.student.students import Students


class Config(BaseModel):
    """
    Représente la configuration utilisateur
    """
    rubric: Rubric
    students: Students

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la configuration de la grille d'évaluation.
        """
        return {
            "grille": self.rubric.to_dict(),
            "étudiants": [student.to_dict() for student in self.students],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """
        Crée une instance validée de Config à partir d'un dictionnaire.
        """
        config = cls(
            rubric=Rubric.from_dict(data["grille"]),
            students=Students(students=[Student.from_dict(student)
                                        for student in data["étudiants"]]),
        )
        return config

    def copy(self) -> "Config": # type: ignore
        """
        Retourne une copie de la configuration.
        """
        return Config(
            rubric=self.rubric.copy(),
            students=self.students.copy()
        )

def read_config(path: str | Path) -> Config:
    """
    Lit la configuration à partir d'un fichier YAML et retourne une instance de Config.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Le fichier de configuration {path} n'existe pas.")

    with open(path, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return Config.from_dict(data)
