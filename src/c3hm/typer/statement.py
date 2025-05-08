from pathlib import Path

import typer

from c3hm.commands.statement import generate_statement_rubric
from c3hm.data.config import Config


def statement_rubric_command(
    config_path: Path = typer.Argument(  # noqa: B008
        Path.cwd(),  # noqa: B008
        help="Répertoire racine contenant les dossiers des étudiants"
    ),
    output_path: Path = typer.Option(  # noqa: B008
        None,  # noqa: B008
        "--output", "-o",
        help="Répertoire de sortie pour les fichiers générés"
    )
):
    """
    Génère la grille d'évaluation à présenter aux élèves à partir du fichier de configuration.
    """
    config = Config.from_yaml(config_path)
    if not output_path:
        output_path = config_path.with_suffix(".docx")
    generate_statement_rubric(config.rubric, output_path, title=config.title())
