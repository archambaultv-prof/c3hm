from pathlib import Path

import click

from c3hm.commands.feedback import generate_feedback
from c3hm.data.config.config_parser import config_from_yaml


@click.command(
    name="feedback",
    help=(
        "Génère un document Word de rétroaction pour les étudiants "
        "à partir d’un fichier de correction."
    )
)
@click.argument(
    "config_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path
    ),
    required=True
)
@click.argument(
    "gradebook_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path
    ),
    required=True
)
@click.option(
    "--output", "-o",
    "output_dir",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        path_type=Path
    ),
    default=None,
    help="Répertoire de sortie pour les fichiers générés"
)
def feedback_command(config_path: Path, gradebook_path: Path, output_dir: Path):
    """
    Génère un document Word de rétroaction pour les étudiants à partir d’une fichier de correction.
    """
    if output_dir is None:
        output_dir = Path.cwd() / "rétroaction"
    config = config_from_yaml(config_path)
    generate_feedback(
        config=config,
        gradebook_path=gradebook_path,
        output_dir=output_dir
    )

