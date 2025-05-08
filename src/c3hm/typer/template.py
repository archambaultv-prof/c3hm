from pathlib import Path

import typer

from c3hm.commands.template import export_template


def template_command(
    output_path: Path = typer.Option(  # noqa: B008
        None,  # noqa: B008
        "--output", "-o",
        help="Chemin vers le fichier de configuration à générer"
    )
):
    """
    TODO: Remplacer par une vraie description
    """
    output_path = Path.cwd() / "grille.yaml" if not output_path else Path(output_path)
    export_template(output_path)
