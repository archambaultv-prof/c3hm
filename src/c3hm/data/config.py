from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel

from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.rubric.rubric import Rubric
from c3hm.data.student.student import Student
from c3hm.data.student.students import Students, read_student
from c3hm.utils.decimal import split_decimal


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

    @classmethod
    def from_user_config(cls, path: str | Path) -> "Config":
        """
        Lit la configuration à partir d'un fichier YAML et retourne une instance de Config.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Le fichier de configuration {path} n'existe pas.")

        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return cls.from_user_dict(path, data)

    @classmethod
    def from_user_dict(cls, data,  path: str | Path | None) -> "Config":
        if "étudiants" not in data:
            s= Students(students=[])
        else:
            path = Path(path) if isinstance(path, str) else path
            s = _normalize_students(data["étudiants"], path)
        r = _normalize_rubric(data["grille"])

        return cls(
            rubric=r,
            students=s
        )

def _normalize_students(students: str  | dict , root: Path | None) -> Students:
    if isinstance(students, str):
        p = Path(students)
        if not p.is_absolute() and root is not None:
            p = Path(root).parent / p
        xs = read_student(p)
        return Students(students=xs)
    return Students(students=[Student.from_dict(student)
                              for student in students])

def _normalize_rubric(rubric: dict) -> Rubric:
    if "format" not in rubric:
        rubric["format"] = {}
    _normalize_id_name_description(rubric["évaluation"])
    _normalize_descriptors(rubric)
    _normalize_points(rubric["évaluation"])
    return Rubric.from_dict(rubric)


def _normalize_descriptors(rubric: dict) -> None:
    """
    Normalise les descripteurs dans la grille d'évaluation.
    Assure que chaque descripteur est défini pour chaque indicateur et niveau de grade.
    """
    if "descripteurs par défaut" in rubric["évaluation"]:
        default = rubric["évaluation"]["descripteurs par défaut"]
        if len(default) != len(rubric["niveaux"]):
            raise ValueError(
                "Le nombre de descripteurs par défaut doit correspondre au nombre de niveaux."
            )
    else:
        default = None

    for criterion in rubric["évaluation"]["critères"]:
        for indicator in criterion["indicateurs"]:
            if "descripteurs" not in indicator:
                if default is None:
                    raise ValueError(
                        f"L'indicateur '{indicator['description']}' du critère "
                        f"'{criterion['nom']}' n'a pas de descripteurs définis et "
                        "aucun descripteur par défaut n'est spécifié."
                    )
                indicator["descripteurs"] = default

    descriptors = {}
    for criterion in rubric["évaluation"]["critères"]:
        for indicator in criterion["indicateurs"]:
            if len(indicator["descripteurs"]) != len(rubric["niveaux"]):
                raise ValueError(
                    f"L'indicateur '{indicator['description']}' du critère "
                    f"'{criterion['nom']}' doit avoir le même nombre de descripteurs que "
                    "le nombre de niveaux dans la grille d'évaluation."
                )
            for i, level in enumerate(rubric["niveaux"]):
                key = (indicator["id"], level["nom"])
                descriptors[key] = indicator["descripteurs"][i]
    rubric["descripteurs"] = descriptors

def _normalize_id_name_description(evaluation: dict) -> None:
    """
    Normalise les identifiants des critères et des indicateurs dans la grille d'évaluation.
    Assure que chaque critère et indicateur a un identifiant unique.
    """
    for i, criterion in enumerate(evaluation["critères"]):
        if "nom" not in criterion:
            raise ValueError(
                f"Le critère {i+1} n'a pas de nom défini. "
                "Chaque critère doit avoir un nom."
            )
        if "id" not in criterion:
            criterion["id"] = f"C{i+1}"
        for j, indicator in enumerate(criterion["indicateurs"]):
            if "description" not in indicator:
                raise ValueError(
                    f"L'indicateur {j+1} du critère '{criterion['nom']}' n'a pas de description "
                    "définie. Chaque indicateur doit avoir une description."
                )
            if "id" not in indicator:
                indicator["id"] = f"C{i+1}_I{j+1}"

def _normalize_points(evaluation: dict) -> None:
    """
    Normalise les points dans la grille d'évaluation. Lève une erreur si les points ne peuvent
    pas être normalisés de manière cohérente.

    L'utilisateur peut spécifier:
    - Un total pour l'ensemble de la grille (rubric["total"]).
    - Un total pour chaque critère (rubric["critères"][i]["total"]).
    - Les points pour chaque indicateur (rubric["critères"][i]["indicateurs"][j]["points"]).

    Cette fonction vérifie la cohérence de ces valeurs. Si certaines sont manquantes et
    peuvent être déduites sans ambiguïté, elles sont ajoutées. Par priorité:
    - Si l'ensemble des points des indicateurs est défini, le total du critère est calculé
      ou validé.
    - Si un total de critère est défini, les indicateurs avec des points manquants
      sont mis à jour pour que la somme des points soit égale au total du critère.
    - Si l'ensemble des points des critères est défini, le total de la grille est calculé
      ou validé.
    - Si le total de la grille est défini, les critères avec des points manquants
      sont mis à jour pour que la somme des points soit égale au total de la grille.

    L'algorithme boucle sur ces quatre étapes jusqu'à ce qu'aucune modification ne soit apportée
    ou que les points soient cohérents.
    """
    grade_step = evaluation.get("pas de notation", Evaluation.grade_step_default)
    if not isinstance(grade_step, Decimal):
        grade_step = Decimal(str(grade_step))

    # Normalisation des clés manquantes
    _initialize_totals(evaluation)

    # Normalisation des points
    while True:
        modified = False

        # Mise à jour du total du critère par les indicateurs ou vice-versa
        modified = _criterion_indicators_total(evaluation, grade_step)

        # Mise à jour du total de l'évaluation par les critères ou vice-versa
        modified = modified or _evaluation_criteria_totals(evaluation, grade_step)

        if not modified:
            # Aucune modification n'a été apportée, on sort de la boucle
            break

    # Vérification que chaque indicateur à des points.
    for criterion in evaluation["critères"]:
        for indicator in criterion["indicateurs"]:
            if indicator["points"] is None:
                raise ValueError(
                    f"L'indicateur '{indicator['description']}' du critère "
                    f"'{criterion['nom']}' n'a pas de points définis "
                    "et ils ne peuvent pas être déduits de la grille d'évaluation."
                )

def _initialize_totals(evaluation):
    if "total" not in evaluation:
        evaluation["total"] = None

    for criterion in evaluation["critères"]:
        if "total" not in criterion:
            criterion["total"] = None
        for indicator in criterion["indicateurs"]:
            if "points" not in indicator:
                indicator["points"] = None

def _evaluation_criteria_totals(evaluation, grade_step) -> bool:
    modified = False

    missing_criteria = [
            criterion for criterion in evaluation["critères"]
            if criterion["total"] is None
        ]
    if len(missing_criteria) == 0:
            # Tous les critères ont un total défini
        pts = [Decimal(str(criterion["total"]))
                   for criterion in evaluation["critères"]
                   if criterion["total"] is not None]
        total_points = sum(pts)
        if evaluation["total"] is None:
            evaluation["total"] = total_points
            modified = True
        elif evaluation["total"] != total_points:
            raise ValueError(
                    "Le total de l'évaluation ne correspond pas à la somme des points des "
                    "critères."
                )
    elif evaluation["total"] is not None:
            # Certains critères n'ont pas de total, mais le total de l'évaluation est défini
        missing_points = Decimal(str(evaluation["total"])) - sum(
                Decimal(str(criterion["total"]))
                for criterion in evaluation["critères"]
                if criterion["total"] is not None
            )
        if missing_points < Decimal(0):
            raise ValueError(
                    "Le total de l'évaluation est inférieur à la somme des points des critères."
                )
        new_pts = split_decimal(
                missing_points,
                len(missing_criteria),
                grade_step
            )
        for x, p in zip(missing_criteria, new_pts, strict=True):
            x["total"] = p
        modified = True
    return modified

def _criterion_indicators_total(evaluation, grade_step) -> bool:
    modified = False

    for criterion in evaluation["critères"]:
        pts = [Decimal(str(indicator["points"]))
                   for indicator in criterion["indicateurs"]
                   if indicator["points"] is not None]
        if len(pts) == len(criterion["indicateurs"]):
                # Tous les indicateurs ont des points définis
            total_points = sum(pts)
            if criterion["total"] is None:
                criterion["total"] = total_points
                modified = True
            elif criterion["total"] != total_points:
                raise ValueError(
                        f"Le total du critère '{criterion['nom']}' ({criterion['total']}) "
                        "ne correspond pas à la somme des points des "
                        f"indicateurs ({total_points})."
                    )
        elif criterion["total"] is not None:
                # Certains indicateurs n'ont pas de points, mais le total du critère est défini
            missing_points = Decimal(str(criterion["total"])) - sum(pts)
            if missing_points < Decimal(0):
                raise ValueError(
                        f"Le total du critère '{criterion['nom']}' ({criterion['total']}) "
                        "est inférieur à la somme des points des indicateurs."
                    )
            missing_indicators = [indicator for indicator in criterion["indicateurs"]
                                      if indicator["points"] is None]
            new_pts = split_decimal(
                    missing_points,
                    len(missing_indicators),
                    grade_step
                )
            for x, p in zip(missing_indicators, new_pts, strict=True):
                x["points"] = p
            modified = True
    return modified
