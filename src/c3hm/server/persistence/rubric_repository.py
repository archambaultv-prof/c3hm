"""
Repository pour la persistence des rubrics (lecture/écriture fichiers JSON).
"""

import json
from pathlib import Path

from c3hm.data.rubric import Rubric


class RubricRepository:
    """
    Encapsule l'accès en lecture/écriture des fichiers JSON de rubrics.

    Principales responsabilités:
    - Charger une rubric JSON
    - Sauvegarder une rubric JSON
    - Lister les rubrics disponibles
    - Valider l'existence des fichiers
    """

    def __init__(self, rubrics_dir: Path):
        """
        Initialise le repository avec le répertoire des rubrics.

        Args:
            rubrics_dir: Chemin vers le répertoire contenant les fichiers JSON
        """
        self.rubrics_dir = rubrics_dir

    def load_rubric(self, filename: str) -> dict:
        """
        Charge les données brutes d'une rubric depuis un fichier JSON.

        Args:
            filename: Nom du fichier (ex: "student.json")

        Returns:
            Dict avec les données JSON brutes

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            json.JSONDecodeError: Si le JSON est invalide
        """
        json_file = self.rubrics_dir / filename
        if not json_file.exists():
            raise FileNotFoundError(f"Rubric file not found: {filename}")

        with open(json_file, encoding="utf-8") as f:
            return json.load(f)

    def save_rubric(self, filename: str, data: dict) -> None:
        """
        Sauvegarde les données d'une rubric dans un fichier JSON.

        Args:
            filename: Nom du fichier (ex: "student.json")
            data: Dict avec les données à sauvegarder

        Raises:
            FileNotFoundError: Si le répertoire n'existe pas
        """
        json_file = self.rubrics_dir / filename
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_rubric_object(self, filename: str) -> Rubric:
        """
        Charge une rubric et retourne un objet Rubric.

        Args:
            filename: Nom du fichier (ex: "student.json")

        Returns:
            Objet Rubric désérialisé

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si la rubric est invalide
        """
        data = self.load_rubric(filename)
        return Rubric.from_dict(data)

    def list_filenames(self) -> list[str]:
        """
        Liste les noms de tous les fichiers JSON de rubrics.

        Returns:
            Liste triée des noms de fichiers
        """
        json_files = sorted(self.rubrics_dir.glob("*.json"))
        return [f.name for f in json_files]

    def file_exists(self, filename: str) -> bool:
        """
        Vérifie si un fichier de rubric existe.

        Args:
            filename: Nom du fichier

        Returns:
            True si le fichier existe
        """
        json_file = self.rubrics_dir / filename
        return json_file.exists()
