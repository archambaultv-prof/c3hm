from pathlib import Path

import click

from c3hm.server import run_server


@click.command(
    name="server",
    help="Lance un serveur web local pour faciliter la correction des travaux."
)

@click.argument(
    "rubrics_dir",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=Path
    ),
    required=True
)

@click.option(
    "--port", "-p",
    type=int,
    default=5000,
    help="Port sur lequel lancer le serveur (défaut: 5000)"
)

def server_command(rubrics_dir: Path, port: int):
    """
    Lance un serveur web local pour la correction interactive des rubrics.
    """
    if not rubrics_dir.is_absolute():
        rubrics_dir = Path.cwd() / rubrics_dir

    # Vérifier qu'il y a des fichiers JSON dans le répertoire
    json_files = list(rubrics_dir.glob("*.json"))
    if not json_files:
        click.echo(f"❌ Aucun fichier JSON trouvé dans {rubrics_dir}", err=True)
        raise click.Abort()

    click.echo(f"🚀 Démarrage du serveur avec {len(json_files)} rubric(s) trouvée(s)...")
    run_server(rubrics_dir=rubrics_dir, port=port)
