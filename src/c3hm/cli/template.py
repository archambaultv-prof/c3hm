from pathlib import Path

import click

from c3hm.commands.template import export_template


@click.command(
    name="template",
    help=(
        "Génère une de grille d'évaluation."
    )
)
@click.option(
    '--output', '-o', 'output_path',
    type=click.Path(path_type=Path),
    default=None,
    help="Chemin vers la grille d'évaluation à générer"
)
@click.option(
    '--levels', '-l', 'nb_levels',
    type=click.IntRange(2, 5),
    default=4,
    help="Indique le nombre de niveaux de performance à inclure dans la grille (entre 2 et 5)."
)
def template_command(output_path: Path,
                     nb_levels: int) -> None:
    """
    Génère une grille d'évaluation.
    """
    if output_path is None:
        output_path = Path.cwd() / "grille.xlsx"
    elif not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    export_template(output_path, nb_levels=nb_levels)
