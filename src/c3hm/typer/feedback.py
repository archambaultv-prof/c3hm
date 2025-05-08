from pathlib import Path

import openpyxl
import typer

from c3hm.commands.feedback import generate_feedback_rubric, grades_from_wb
from c3hm.data.config import Config


def feedback_command(
    config_path: Path = typer.Argument(  # noqa: B008
        Path.cwd(),  # noqa: B008
        help="Répertoire racine contenant les dossiers des étudiants"
    ),
    gradebook_path: Path = typer.Argument(  # noqa: B008
        Path.cwd(),  # noqa: B008
        help="Répertoire racine contenant les dossiers des étudiants"
    ),
    output_dir: Path = typer.Option(  # noqa: B008
        None,  # noqa: B008
        "--output", "-o",
        help="Répertoire de sortie pour les fichiers générés"
    )
):
    """
    TODO: Remplacer par une vraie description
    """
    config = Config.from_yaml(config_path)
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    graded_rubrics = grades_from_wb(wb, config)

    # Génère le document Word
    for graded_rubric in graded_rubrics:
        # Copie le fichier dans le répertoire de sortie pour inspection manuelle
        filename = f"{graded_rubric.student.omnivox_code} - {graded_rubric.student.alias}.docx"
        feedback_path = output_dir / filename
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        title = (graded_rubric.student.first_name + " " +
                 graded_rubric.student.last_name + " - " +
                 config.evaluation.name + " - " +
                 config.evaluation.course)
        generate_feedback_rubric(graded_rubric, feedback_path, title=title)

