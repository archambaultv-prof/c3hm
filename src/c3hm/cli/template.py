from pathlib import Path

import click

from c3hm.commands.template import export_template


@click.command(
    name="template",
    help=(
        "Génère un fichier de configuration."
    )
)
@click.option(
    '--output', '-o', 'output_path',
    type=click.Path(path_type=Path),
    default=None,
    help="Chemin vers le fichier de configuration à générer"
)
@click.option(
    '--levels', '-l', 'nb_levels',
    type=click.IntRange(2, 5),
    default=5,
    help="Indique le nombre de niveaux de performance à inclure dans le modèle de configuration."
)
def template_command(output_path: Path,
                     nb_levels: int) -> None:
    """
    Génère un fichier de configuration commenté.
    """
    if output_path is None:
        output_path = Path.cwd() / "grille.yaml"
    elif not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    export_template(output_path, nb_levels=nb_levels)
