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
    "--output", "-o",
    "output_dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Répertoire de sortie pour les fichiers générés",
    default=None
)
def gradebook_command(rubric_path: Path, students: Path | None, output_dir: Path | None):
    """
    Génère les grilles de correction à partir d'un modèle et d'une liste d'étudiants.
    """
    if not output_dir:
        output_dir = Path.cwd() / Path("grilles de correction")
    if output_dir.exists():
        raise FileExistsError(f"Le répertoire {output_dir} existe déjà.")
    if not rubric_path.is_absolute():
        rubric_path = Path.cwd() / rubric_path
    if students and not students.is_absolute():
        students = Path.cwd() / students
    generate_gradebook(
        rubric=rubric_path,
        output_dir=output_dir,
        students_file=students,
    )
