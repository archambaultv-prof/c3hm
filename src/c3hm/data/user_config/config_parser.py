from pathlib import Path

import yaml

from c3hm.data.user_config.config import UserConfig


def config_from_yaml(yaml_path: Path | str) -> UserConfig:
        """
        Charge la configuration à partir d'un fichier YAML.
        """
        yaml_path = Path(yaml_path)
        with open(yaml_path, encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        c = config_from_user_dict(config_dict)
        # Si le chemin du fichier etudiants est relatif, le convertir en absolu
        # avec racine le yaml_path.
        if not c.students.is_absolute():
            c.students = (yaml_path.parent / c.students).resolve()
        return c

def config_from_user_dict(user_dict: dict) -> UserConfig:
    """
    Charge la configuration à partir d'un dictionnaire utilisateur.
    """
    # Étape 1: Changer les clés pour correspondre au modèle Pydantic
    rename_dict = {
        "id": "excel_id",
        "évaluation": "evaluation",
        "orientation": "orientation",
        "format": "format",
        "étudiants": "students",
        "maximum": "maximum",
        "minimum": "minimum",
        "points": "points",
        "pas pour inférence des points": "points_inference_step",
        "total": "points_total",
        "total nb de décimales": "points_total_nb_of_decimal",
        "niveaux": "grade_levels",
        "critères": "criteria",
        "nom": "name",
        "indicateurs": "indicators",
        "descripteurs": "descriptors",
        "indicateur": "name",
        "critère": "name",
        "afficher les points des indicateurs": "show_indicators_points",
        "largeur des colonnes": "columns_width",
        "largeur des colonnes avec commentaires": "columns_width_comments",
        "afficher la description du niveau": "show_grade_level_descriptions"
    }
    d = _rename_keys(user_dict, rename_dict)

    # Étape 2: Convertir le dictionnaire en instance de Config
    return UserConfig(**d)

def _rename_keys(user_dict: dict, rename_dict: dict) -> dict:
    """
    Renomme les clés d'un dictionnaire en utilisant un dictionnaire de renommage.
    """
    d = {}
    for k, v in user_dict.items():
        new_k = rename_dict[k]
        if isinstance(v, dict):
            d[new_k] = _rename_keys(v, rename_dict)
        elif isinstance(v, list):
            d[new_k] = _process_list(v, rename_dict)
        else:
            d[new_k] = v

    return d


def _process_list(items: list, rename_dict: dict) -> list:
    """
    Traite récursivement une liste, en renommant les clés des dictionnaires
    et en gérant les listes imbriquées.
    """
    result = []
    for item in items:
        if isinstance(item, dict):
            result.append(_rename_keys(item, rename_dict))
        elif isinstance(item, list):
            result.append(_process_list(item, rename_dict))
        else:
            result.append(item)
    return result
