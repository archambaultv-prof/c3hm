from pathlib import Path

from c3hm.data.config import Config


def export_template(output_path: Path,
                    nb_levels: int = 5) -> None:
    """
    Génère un fichier de configuration
    """
    config = Config.default(nb_levels=nb_levels)
    config.yaml_dump(output_path)
