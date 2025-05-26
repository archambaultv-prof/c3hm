"""
Ce module contient les fonctions en lien avec Omnivox.
"""

from pathlib import Path


def extract_student_info(folder_name: str | Path) -> str | None:
    """
    Extrait la partie du nom de dossier qui correspond au NOM1_NOM2_12345.

    Le nom du dossier doit suivre la convention de nommage Omnivox pour les étudiants,
    qui est :
    - Un ou plusieurs noms de famille (lettres se terminant par un underscore)
    - Un numéro composé uniquement de chiffres se terminant par un underscore

    Si le nom du dossier ne correspond pas à ce modèle, retourne None.
    """

    if isinstance(folder_name, Path):
        folder_name = folder_name.name

    sub_parts = folder_name.split("_")
    student_info = []
    for part in sub_parts:
        if part.isdigit():
            if not student_info:
                # Si la première partie est un numéro, ce n'est pas un dossier étudiant
                return None
            student_info.append(part)
            return "_".join(student_info)
        else:
            student_info.append(part)
    # If we reach here, it means the folder name does not match the expected
    # pattern
    return None


def is_student_folder(folder_name: str | Path) -> bool:
    """
    Vérifie si le nom du dossier correspond au format étudiant Omnivox.
    """
    return extract_student_info(folder_name) is not None
