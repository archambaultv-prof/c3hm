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

def template_command(output_path: Path) -> None:
    """
    Génère une grille d'évaluation.
    """
    if output_path is None:
        output_path = Path.cwd() / "grille.yaml"
    elif not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    export_template(output_path)
