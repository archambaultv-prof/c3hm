import yaml
from pydantic import BaseModel, Field

from c3hm.data.evaluation import Evaluation
from c3hm.data.rubric import Rubric
from c3hm.data.student import Student


class Config(BaseModel):
    """
    Représente une grille d'évaluation pour un cours et une évaluation spécifiques.
    """
    evaluation: Evaluation
    rubric: Rubric
    students: list[Student] = Field(
        default_factory=list,
        min_length=0
    )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant la configuration de la grille d'évaluation.
        """
        return {
            "évaluation": self.evaluation.to_dict(),
            "grille": self.rubric.to_dict(),
            "étudiants": [student.to_dict() for student in self.students],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """
        Crée une instance validée de Config à partir d'un dictionnaire.
        """
        config = cls(
            evaluation=Evaluation.from_dict(data["évaluation"]),
            rubric=Rubric.from_dict(data["grille"]),
            students=[Student.from_dict(student) for student in data["étudiants"]],
        )
        config.validate_config()
        return config

    def title(self) -> str:
        """
        Retourne le titre de la grille d'évaluation.

        Le titre est formé du nom du cours et de l'évaluation, séparés par un tiret.
        """
        endash = "\u2013"
        title = "Grille d'évaluation"
        if self.evaluation.course:
            title += f" {endash} {self.evaluation.course}"
        if self.evaluation.name:
            title += f" {endash} {self.evaluation.name}"
        return title

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """
        Crée une instance de Config à partir d'un fichier YAML.
        """
        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data)

    def to_yaml(self, path: str) -> None:
        """
        Sauvegarde la configuration dans un fichier YAML.
        """
        with open(path, "w", encoding="utf-8") as file:
            yaml.dump(self.to_dict(), file, allow_unicode=True,
                      sort_keys=False)

    def validate_config(self) -> None:
        """
        Valide la grille d'évaluation et les étudiants.

        Voir la méthode validate de Rubric pour les détails de la validation.
        """
        self.rubric.validate()

    def find_student(self, omnivox_code: str) -> Student | None:
        """
        Trouve un étudiant dans la configuration à partir de son code omnivox.
        """
        for student in self.students:
            if student.omnivox_code == omnivox_code:
                return student
        return None
