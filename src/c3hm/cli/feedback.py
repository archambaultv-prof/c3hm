import shutil
from pathlib import Path

import click

from c3hm.commands.feedback import generate_feedback


@click.command(
    name="feedback",
    help=("Génère un document PDF de rétroaction pour les étudiants à partir des fichiers de correction."),
)
@click.argument(
    "gradebook", type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path), required=True
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Répertoire de sortie pour les fichiers générés",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force la régénération des fichiers de rétroaction en supprimant "
         "les fichiers existants dans le répertoire de sortie",
)
@click.option(
    "--replace",
    "-r",
    is_flag=True,
    help="Remplace les fichiers de rétroaction existants sans supprimer "
         "les autres fichiers dans le répertoire de sortie",
)

def feedback_command(gradebook: Path, output_dir: Path, force: bool, replace: bool) -> None:
    """
    Génère un document rétroaction pour les étudiants à partir d’une fichier de correction.
    """
    if force and replace:
        raise ValueError("Les options --force et --replace ne peuvent pas être utilisées ensemble.")
    if not gradebook.is_absolute():
        gradebook = Path.cwd() / gradebook
    if output_dir is None:
        parent = gradebook.parent if gradebook.is_file() else gradebook
        output_dir = parent / Path("rétroaction")
    if output_dir.exists():
        if force:
            for item in output_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        elif replace:
            pass # Nothing to do, we will overwrite existing files as needed
        else:
            raise FileExistsError(f"Le répertoire {output_dir} existe déjà.")
    generate_feedback(
        gradebook_path=gradebook,
        output_dir=output_dir,
    )
