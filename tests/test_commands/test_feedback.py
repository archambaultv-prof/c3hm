from pathlib import Path

import openpyxl
import yaml

from c3hm.commands.feedback import grades_from_wb
from c3hm.commands.generate_rubric import generate_rubric
from c3hm.data.config import Config
from c3hm.data.rubric import CTHM_OMNIVOX


def test_graded_rubrics_from_wb(
    config_template_path: Path,
    gradebook_path: Path,
):
    """
    Teste la fonction grades_from_wb.
    """

    # Charge la configuration et la grille d'évaluation
    config = Config.from_yaml(config_template_path)

    # Ouvre le gradebook
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config)

    # Vérifie que le nombre est correct
    assert len(grades) == 3


def test_generate_feedback_rubric(
    config_template_path: Path,
    gradebook_path: Path,
    output_dir: Path
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’un grille d’évaluation (GradedRubric).
    """

    config = Config.from_yaml(config_template_path)
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config)

    # Génère le document Word
    for grade in grades:
        student = config.find_student(grade[CTHM_OMNIVOX])
        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / "graded rubrick"
        feedback_path = feedback_path / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        title = (student.first_name + " " +
                 student.last_name + " - " +
                 config.evaluation.name + " - " +
                 config.evaluation.course)
        generate_rubric(config.rubric, feedback_path, title=title, grades=grade)
