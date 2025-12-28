from pathlib import Path

import click

from c3hm.commands.rubric import export_rubric


@click.command(
    name="rubric",
    help=(
        "Génère une de grille d'évaluation PDF à partir d’un fichier de configuration json."
    )
)
@click.argument(
    'input_path',
    type=click.Path(path_type=Path),
    required=True
)
@click.option(
    '--output', '-o', 'output_path',
    type=click.Path(path_type=Path),
    default=None,
    help="Chemin vers la grille d'évaluation PDF à générer"
)

def rubric_command(input_path: Path, output_path: Path) -> None:
    """
    Génère une grille d'évaluation PDF à partir d’un fichier de configuration json.
    """
    if output_path is None:
        output_path = Path.cwd() / "grille.pdf"
    elif not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    export_rubric(input_path, output_path)
