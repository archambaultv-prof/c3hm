from pathlib import Path

import click

from c3hm.commands.gradebook import generate_gradebook
from c3hm.data.config_parser import parse_user_config


@click.command(
    name="gradebook",
    help=(
        "Génère les grilles de correction à partir du fichier de configuration."
    )
)
@click.argument(
    "config_path",
    type=click.Path(file_okay=True, dir_okay=False, exists=True, path_type=Path),
    required=True
)
@click.argument(
    "students_file",
    type=click.Path(file_okay=True, dir_okay=False, exists=True, path_type=Path),
    required=True
)
@click.option(
    "--output", "-o",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Répertoire de sortie pour les fichiers générés",
    default=None
)
def gradebook_command(config_path: Path, students_file: Path, output_dir: Path | None):
    """
    Génère les grilles de correction à partir du fichier de configuration.
    """
    config = parse_user_config(config_path)
    if not output_dir:
        output_dir = Path.cwd() / Path("grilles de correction")
    generate_gradebook(config, students_file, output_dir)
