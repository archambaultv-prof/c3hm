from pathlib import Path

import click

from c3hm.commands.template import export_template


@click.command(
    name="template",
    help=(
        "Génère une de grille d'évaluation sous format TOML."
    )
)
@click.option(
    '--output', '-o', 'output_path',
    type=click.Path(path_type=Path),
    default=None,
    help="Chemin vers la grille d'évaluation à générer"
)
@click.option(
    '--force', '-f', 'force',
    is_flag=True,
    default=False,
    help="Force l'écrasement du fichier de sortie s'il existe"
)

def template_command(output_path: Path, force: bool) -> None:
    """
    Génère une grille d'évaluation.
    """
    original_output_path = output_path
    if output_path is None:
        output_path = Path.cwd() / "grille.yaml"
        original_output_path = output_path
    elif not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    if output_path.exists() and not force:
        raise FileExistsError(f"Le fichier {original_output_path} existe déjà. Utilisez -f pour l'écraser.")
    export_template(output_path)
