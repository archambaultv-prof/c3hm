from importlib import resources

import yaml

from c3hm.data.config import Config


def export_template(
        *,
        config: Config | None = None,
        output_path: str = "grille.yaml",
        template: str = "default") -> None:
    """
    Exporte le modèle de configuration vers un fichier YAML.
    """
    if config is None:
        config = resources.files("c3hm.assets.templates.config").joinpath("config_5_levels.yaml")
    yaml_dict = config.to_dict()
    match template:
        case "default":
            strip_default(yaml_dict)
        case "basic":
            strip_basic(yaml_dict)
        case "full":
            pass  # Nothing to do here
        case _:
            raise ValueError(f"Modèle '{template}' non reconnu.")

    # Écrit la configuration dans le fichier YAML
    with open(output_path, "w", encoding="utf-8") as file:
        yaml.dump(yaml_dict, file, allow_unicode=True)


def strip_default(d: dict) -> dict:
    """
    Supprime les valeurs non voulues par la configuration par défaut.
    """
    d["évaluation"]["nom"] = None
    d["évaluation"]["cours"] = None
    d["grille"]["critères"] = []
    d["étudiants"] = []


def strip_basic(d: dict) -> dict:
    """
    Supprime les valeurs non voulues par la configuration basique.
    """
    strip_default(d)
    d["échelle"]["niveaux"] = []
