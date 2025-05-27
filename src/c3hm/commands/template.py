import shutil
from importlib import resources
from pathlib import Path


def export_template(output_path: Path | str = "grille.yaml",
                    template: str = "grille.yaml") -> None:
    """
    Copie la configuration d'exemple.
    """
    config_path = (resources
                    .files("c3hm.assets.templates.config")
                    .joinpath(template))
    config_path = Path(config_path) # type: ignore

    output_path = Path(output_path)

    shutil.copy(config_path, output_path)

