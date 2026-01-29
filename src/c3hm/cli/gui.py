from pathlib import Path

import click

from c3hm.commands.gui import launch_gui


@click.command(
    name="gui",
    help=(
        "Ouvre une interface graphique pour corriger une grille JSON."
    )
)
@click.argument(
    "gradebook_path",
    type=click.Path(file_okay=True, dir_okay=False, exists=True, path_type=Path),
    required=True
)
def gui_command(gradebook_path: Path) -> None:
    """
    Ouvre une interface graphique pour corriger une grille JSON.
    """
    if not gradebook_path.is_absolute():
        gradebook_path = Path.cwd() / gradebook_path
    launch_gui(gradebook_path)
