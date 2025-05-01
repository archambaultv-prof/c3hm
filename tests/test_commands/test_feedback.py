from pathlib import Path

import openpyxl

from c3hm.commands.feedback import generate_feedback_rubric, graded_rubrics_from_wb
from c3hm.data.config import Config


def test_graded_rubrics_from_wb(
    config_1_path: Path,
    gradebook_1_path: Path,
    output_dir: Path
):
    """
    Teste la fonction graded_rubrics_from_wb.
    """

    # Charge la configuration et la grille d'évaluation
    config = Config.from_yaml(config_1_path)

    # Ouvre le gradebook
    wb = openpyxl.load_workbook(gradebook_1_path,
                                data_only=True,
                                read_only=True)
    graded_rubrics = graded_rubrics_from_wb(wb, config)

    # Vérifie que le nombre de GradedRubric est correct
    assert len(graded_rubrics) == 3

    # Copie les GradedRubric dans le dossier de sortie
    for gr in graded_rubrics:
        gr_path = output_dir / "graded rubrick" / f"{gr.student.ws_name()}.yaml"
        gr_path.parent.mkdir(parents=True, exist_ok=True)
        gr.to_yaml(gr_path)

def test_generate_feedback_rubric(
    config_1_path: Path,
    gradebook_1_path: Path,
    output_dir: Path
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’un grille d’évaluation (GradedRubric).
    """

    config = Config.from_yaml(config_1_path)
    wb = openpyxl.load_workbook(gradebook_1_path,
                                data_only=True,
                                read_only=True)
    graded_rubrics = graded_rubrics_from_wb(wb, config)

    # Génère le document Word
    for graded_rubric in graded_rubrics:
        # Copie le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / "graded rubrick" / f"{graded_rubric.student.ws_name()}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        title = (graded_rubric.student.first_name + " " +
                 graded_rubric.student.last_name + " - " +
                 config.evaluation.name + " - " +
                 config.evaluation.course)
        generate_feedback_rubric(graded_rubric, feedback_path, title=title)
