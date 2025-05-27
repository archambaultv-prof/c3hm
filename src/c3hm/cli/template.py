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
@click.option(
    '--full', 'full_template',
    is_flag=True,
    default=False,
    help="Génère un gabarit complet avec toutes les options possibles. "
)
def template_command(output_path: Path,
                     full_template: bool) -> None:
    """
    Génère un fichier de configuration commenté.
    """
    template = "grille.yaml" if full_template else "grille_minimal.yaml"
    output_path = Path.cwd() / ("grille.yaml" if not output_path else Path(output_path))
    export_template(output_path, template=template)
