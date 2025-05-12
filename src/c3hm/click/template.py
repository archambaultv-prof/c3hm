from pathlib import Path

import click
from c3hm.commands.template import export_template


@click.command(
    name="template",
    help=(
        "Génère un fichier de configuration commenté."
    )
)
@click.option(
    '--output', '-o', 'output_path',
    type=click.Path(path_type=Path),
    default=None,
    help="Chemin vers le fichier de configuration à générer"
)
def template_command(output_path: Path):
    """
    Génère un fichier de configuration commenté.
    """
    output_path = Path.cwd() / ("grille.yaml" if not output_path else Path(output_path))
    export_template(output_path)
