"""
Blueprint pour les routes liées aux étudiants.
"""

import json
from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template

from c3hm.data.rubric import Rubric

students_bp = Blueprint("students", __name__)


def scan_rubrics(rubrics_dir: Path) -> list[dict]:
    """
    Scanne le répertoire de rubrics et extrait les informations des étudiants.

    Args:
        rubrics_dir: Répertoire contenant les fichiers JSON des rubrics

    Returns:
        Liste de dictionnaires contenant les informations des étudiants:
        - filename: nom du fichier JSON
        - student_name: nom complet de l'étudiant (prénom + nom)
        - first_name: prénom de l'étudiant
        - last_name: nom de famille de l'étudiant
        - graded: True si la rubric a au moins un indicateur noté
    """
    json_files = sorted(rubrics_dir.glob("*.json"))
    students = []

    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            rubric = Rubric.from_dict(data)

            # Vérifier si l'étudiant existe dans la rubric
            if rubric.student is None:
                continue

            # Déterminer si la rubric est corrigée (utiliser la méthode is_graded de Grid)
            graded = rubric.grid.is_graded()

            students.append(
                {
                    "filename": json_file.name,
                    "student_name": f"{rubric.student.firstname} {rubric.student.surname}",
                    "first_name": rubric.student.firstname,
                    "last_name": rubric.student.surname,
                    "omnivox_id": rubric.student.omnivox_id,
                    "graded": graded,
                }
            )

        except Exception as e:
            # En cas d'erreur, on ignore ce fichier mais on continue
            print(f"⚠️  Erreur lors du traitement de {json_file.name}: {e}")

    return students


@students_bp.route("/")
def index():
    """Page d'accueil avec la liste des étudiants."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    students_data = scan_rubrics(rubrics_dir)

    return render_template(
        "index.html",
        students=students_data,
        rubrics_dir=str(rubrics_dir),
        total_count=len(students_data),
        graded_count=sum(1 for s in students_data if s["graded"]),
        ungraded_count=sum(1 for s in students_data if not s["graded"]),
    )


@students_bp.route("/api/students")
def api_students():
    """API pour obtenir la liste des étudiants en JSON."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    students_data = scan_rubrics(rubrics_dir)
    return jsonify(students_data)
