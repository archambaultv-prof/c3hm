from pathlib import Path

import openpyxl

from c3hm.commands.feedback import generate_feedback, grades_from_wb
from c3hm.data.config.config import Config


def test_graded_rubrics_from_wb(
    config_full_template: Config,
    gradebook_path: Path,
):
    """
    Teste la fonction grades_from_wb.
    """

    # Charge la configuration et la grille d'évaluation
    config = config_full_template
    students = config.students

    # Ouvre le gradebook
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config, students=students)

    # Vérifie que le nombre est correct
    assert len(grades) == 3

def test_graded_rubrics_from_wb_inference(
    config_full_template: Config,
    gradebook2_path: Path,
):
    """
    Teste la fonction grades_from_wb.
    """

    # Charge la configuration et la grille d'évaluation
    config = config_full_template
    students = config.students

    # Ouvre le gradebook
    wb = openpyxl.load_workbook(gradebook2_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config, students=students)

    # Vérifie que le nombre est correct
    assert len(grades) == 3

def test_generate_feedback_rubric(
    config_full_template: Config,
    gradebook_path: Path,
    output_dir: Path
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’un grille d’évaluation (GradedRubric).
    """

    generate_feedback(
        config=config_full_template,
        gradebook_path=gradebook_path,
        output_dir=output_dir / "feedback"
    )
