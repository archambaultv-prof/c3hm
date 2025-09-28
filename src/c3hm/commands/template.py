from pathlib import Path

import yaml

from c3hm.data.config import Config


def export_template(output_path: Path,
                    nb_levels: int = 5) -> None:
    """
    Génère un fichier de configuration
    """
    config = Config.default(nb_levels=nb_levels)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(mode="json"), f,
                  sort_keys=False, allow_unicode=True,
                  indent=2)
