from pathlib import Path

import click

from c3hm.commands.gradebook import generate_gradebook


@click.command(
    name="gradebook",
    help=(
        "Génère les grilles de correction à partir d'un modèle et d'une liste d'étudiants."
    )
)
@click.argument(
    "rubric_path",
    type=click.Path(file_okay=True, dir_okay=False, exists=True, path_type=Path),
    required=True
)
@click.option(
    "-s", "--students",
    type=click.Path(file_okay=True, dir_okay=False, exists=True, path_type=Path),
    help="Fichier contenant la liste des étudiants",
    default=None
)
@click.option(
    "-t", "--teams",
    type=int,
    help="Nombre d'équipes",
    default=None
)
@click.option(
    "--output", "-o",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Répertoire de sortie pour les fichiers générés",
    default=None
)
def gradebook_command(rubric_path: Path, students: Path | None, teams: int | None, output_dir: Path | None):
    """
    Génère les grilles de correction à partir d'un modèle et d'une liste d'étudiants.
    """
    if not output_dir:
        output_dir = Path.cwd() / Path("grilles de correction")
    if not rubric_path.is_absolute():
        rubric_path = Path.cwd() / rubric_path
    if not students and not teams:
        raise ValueError("Vous devez fournir un fichier d'étudiants ou le nombre d'équipes.")
    if students and teams:
        raise ValueError("Vous ne pouvez pas fournir à la fois un fichier d'étudiants et le nombre d'équipes.")
    if students and not students.is_absolute():
        students = Path.cwd() / students
    generate_gradebook(
        rubric=rubric_path,
        students_file=students,
        teams=teams,
        output_dir=output_dir
    )
