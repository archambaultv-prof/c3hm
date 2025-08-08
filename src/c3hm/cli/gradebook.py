from pathlib import Path

import click

from c3hm.commands.gradebook import generate_gradebook
from c3hm.data.config.config_parser import config_from_yaml


@click.command(
    name="gradebook",
    help=(
        "Génère un fichier Excel de correction à "
        "partir d’un fichier de configuration."
    )
)
@click.argument(
    "config_path",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    required=True
)
@click.option(
    "--output", "-o",
    "output_path",
    type=click.Path(),
    help="Répertoire de sortie pour les fichiers générés",
    default=None
)
def gradebook_command(config_path: Path, output_path: Path | None):
    """
    Génère un fichier Excel de correction à partir d’un fichier de configuration.
    """
    config = config_from_yaml(config_path)
    output_path = Path(config_path).with_suffix(".xlsx") if not output_path else Path(output_path)
    generate_gradebook(config, output_path)
