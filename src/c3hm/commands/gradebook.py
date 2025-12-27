import copy
from pathlib import Path

import yaml

from c3hm.data.student import read_omnivox_students_file


def generate_gradebook(rubric: Path, students_file: Path | None, teams: int | None, output_dir: Path) -> None:
    """
    Génère les grilles de correction à partir du fichier de configuration.
    """
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    with open(rubric, encoding="utf-8") as f:
        content = f.read()
    rubric_data = yaml.safe_load(content)

    if students_file:
        generate_gradebook_from_students_file(rubric_data, students_file, output_dir)
    elif teams:
        generate_gradebook_from_teams(rubric_data, teams, output_dir)
    else:
        raise ValueError("Vous devez fournir un fichier d'étudiants ou le nombre d'équipes.")

def generate_gradebook_from_students_file(rubric: dict, students_file: Path, output_dir: Path) -> None:
    students = read_omnivox_students_file(students_file)
    for student in students:
        new_d = {"étudiant": {"nom": f"{student.full_name()}",
                              "matricule": f"{student.omnivox_id}"}}
        new_d.update(copy.deepcopy(rubric))
        d = new_d
        update_criteria(d)
        add_global_comment(d)
        stem = f"{student.last_name} {student.first_name} {student.omnivox_id}.yaml"
        destination = output_dir / stem
        with open(destination, "w", encoding="utf-8") as f:
            yaml.dump(d, f, allow_unicode=True, indent=4, sort_keys=False)

def generate_gradebook_from_teams(rubric: dict, teams: int, output_dir: Path) -> None:
    new_rubric = {"étudiants": [{"nom": None}, {"nom": None}, {"nom": None}, {"nom": None}]}
    new_rubric.update(copy.deepcopy(rubric))
    rubric = new_rubric
    update_criteria(rubric)
    add_global_comment(rubric)
    for team_number in range(1, teams + 1):
        stem = f"Équipe {team_number}.yaml"
        destination = output_dir / stem
        with open(destination, "w", encoding="utf-8") as f:
            yaml.dump(rubric, f, allow_unicode=True, indent=4, sort_keys=False)

def add_global_comment(d: dict) -> None:
    d["commentaire"] = None

def update_criteria(d: dict) -> None:
    for node in d["critères"]:
        if not isinstance(node, dict):
            continue
        if "section" in node:
            continue
        node["note"] = None
        node["commentaire"] = None
