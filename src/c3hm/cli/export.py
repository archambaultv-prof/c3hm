from pathlib import Path

import click

from c3hm.commands.export.export import export_rubric
from c3hm.data.config.config import Config
from c3hm.data.config.config_parser import config_from_yaml


@click.command(
    name="export",
    help=(
        "Génère la grille d'évaluation à présenter "
        "aux élèves à partir du fichier de configuration."
    )
)
@click.argument(
    "config_path",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    required=True
)
@click.option(
    "--output", "-o",
    "output_path",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    help="Nom du fichier de sortie",
    default=None
)

def export_rubric_command(config_path: Path, output_path: Path | None):
    """
    Génère la grille d'évaluation à présenter aux élèves à partir du fichier de configuration.
    """
    config = config_from_yaml(config_path)
    if not output_path:
        output_path = config_path.with_suffix(".docx")
    export_rubric(config, output_path)
