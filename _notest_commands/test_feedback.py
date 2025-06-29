from pathlib import Path

import openpyxl

from c3hm.commands.feedback import generate_feedback, grades_from_wb
from c3hm.data.config import Config


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

    generate_feedback(
        config_path=config_template_path,
        gradebook_path=gradebook_path,
        output_dir=output_dir / "feedback"
    )
