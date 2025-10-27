from pathlib import Path

import click

from c3hm.commands.feedback import generate_feedback


@click.command(
    name="feedback",
    help=(
        "Génère un document Word de rétroaction pour les étudiants "
        "à partir des fichiers de correction."
    )
)

@click.argument(
    "gradebook_dir",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
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
def feedback_command(gradebook_dir: Path, output_dir: Path):
    """
    Génère un document Word de rétroaction pour les étudiants à partir d’une fichier de correction.
    """
    if output_dir is None:
        output_dir = Path.cwd() / Path("grilles de correction")
    if not gradebook_dir.is_absolute():
        gradebook_dir = Path.cwd() / gradebook_dir
    generate_feedback(
        gradebook_path=gradebook_dir,
        output_dir=output_dir
    )

