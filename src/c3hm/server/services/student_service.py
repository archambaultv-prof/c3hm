"""
Service pour indexer et rechercher des étudiants.
"""

import json
from pathlib import Path

from c3hm.data.rubric import Rubric


class StudentService:
    """
    Fournit des utilitaires pour indexer et rechercher des étudiants par ID.

    Maintient un cache de l'index pour améliorer les performances.
    """

    def __init__(self, rubrics_dir: Path):
        """
        Initialise le service avec le répertoire des rubrics.

        Args:
            rubrics_dir: Chemin vers le répertoire contenant les fichiers JSON
        """
        self.rubrics_dir = rubrics_dir
        self._index_cache: dict[str, Path] | None = None

    def build_index(self, use_cache: bool = True) -> dict[str, Path]:
        """
        Construit un index {omnivox_id: chemin_fichier} de tous les étudiants.

        Args:
            use_cache: Si True, utilise le cache si disponible

        Returns:
            Dict mappe omnivox_id (matricule) vers le chemin du fichier JSON
        """
        if use_cache and self._index_cache is not None:
            return self._index_cache

        index: dict[str, Path] = {}
        for json_file in self.rubrics_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                rubric = Rubric.from_dict(data)
                if rubric.student is None:
                    continue
                if rubric.student.omnivox_id:
                    index[rubric.student.omnivox_id] = json_file
            except Exception:
                continue

        if use_cache:
            self._index_cache = index

        return index

    def get_student_file(self, omnivox_id: str) -> Path | None:
        """
        Obtient le chemin du fichier pour un étudiant par ID.

        Args:
            omnivox_id: L'ID Omnivox (matricule) de l'étudiant

        Returns:
            Path vers le fichier JSON, ou None si non trouvé
        """
        index = self.build_index()
        return index.get(omnivox_id)

    def clear_cache(self) -> None:
        """Vide le cache d'index (utile si les fichiers ont été modifiés)."""
        self._index_cache = None
