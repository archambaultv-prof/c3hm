"""
Service pour gérer la synchronisation des coéquipiers.
"""

import json
from pathlib import Path

from c3hm.data import (
    JSON_KEY_FIRSTNAME,
    JSON_KEY_LASTNAME,
    JSON_KEY_OMNIVOX_ID,
    JSON_KEY_TEAMMATES,
)


class TeammateManager:
    """
    Gère la synchronisation bidirectionnelle des coéquipiers entre fichiers de rubrics.

    Logique:
    - Lorsqu'un étudiant ajoute des coéquipiers, tous les coéquipiers doivent
      avoir la même liste mutuelle (cohérence bidirectionnelle)
    - Lorsqu'un coéquipier est retiré, il faut nettoyer les références
      dans les autres fichiers pour éviter les liens non mutuels
    """

    def __init__(self, rubrics_dir: Path):
        """
        Initialise le gestionnaire avec le répertoire des rubrics.

        Args:
            rubrics_dir: Chemin vers le répertoire contenant les fichiers JSON
        """
        self.rubrics_dir = rubrics_dir

    def normalize_teammates(self, teammates: list[dict]) -> list[dict]:
        """
        Normalise la liste des coéquipiers du format API vers le format JSON.

        Du format API:
            {"first_name": "...", "last_name": "...", "omnivox_id": "..."}

        Au format JSON:
            {"prénom": "...", "nom": "...", "matricule": "..."}
        """
        normalized = []
        for tm in teammates:
            normalized.append(
                {
                    JSON_KEY_FIRSTNAME: tm.get("first_name", ""),
                    JSON_KEY_LASTNAME: tm.get("last_name", ""),
                    JSON_KEY_OMNIVOX_ID: tm.get("omnivox_id", ""),
                }
            )
        return normalized

    def _build_student_index(self) -> dict[str, Path]:
        """
        Construit un index {omnivox_id: chemin_fichier} de tous les étudiants.

        Returns:
            Dict mappe omnivox_id (matricule) vers le chemin du fichier JSON
        """
        from c3hm.data.rubric import Rubric

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
        return index

    def _teammate_id(self, entry: dict) -> str:
        """Extrait l'ID d'un coéquipier en toute sécurité."""
        return (entry.get(JSON_KEY_OMNIVOX_ID) or "").strip()

    def sync_teammates(
        self,
        current_student: dict,
        new_teammates: list[dict],
        old_teammates: list[dict],
    ) -> None:
        """
        Synchronise les coéquipiers pour assurer la cohérence mutuelle.

        1. Met à jour tous les coéquipiers sélectionnés pour qu'ils aient la même liste
        2. Nettoie les anciens coéquipiers retirés pour éviter les liens non mutuels

        Args:
            current_student: Dict avec "matricule", "prénom", "nom" de l'étudiant courant
            new_teammates: Liste normalisée des nouveaux coéquipiers
            old_teammates: Liste normalisée des anciens coéquipiers
        """
        current_id = (current_student.get(JSON_KEY_OMNIVOX_ID) or "").strip()
        if not current_id:
            return

        student_index = self._build_student_index()

        new_ids = {self._teammate_id(tm) for tm in new_teammates if self._teammate_id(tm)}
        old_ids = {self._teammate_id(tm) for tm in old_teammates if self._teammate_id(tm)}
        team_ids = new_ids | {current_id}

        # Constituer la list complète avec l'étudiant courant + ses coéquipiers
        team_members = [
            {
                JSON_KEY_FIRSTNAME: current_student.get(JSON_KEY_FIRSTNAME, ""),
                JSON_KEY_LASTNAME: current_student.get(JSON_KEY_LASTNAME, ""),
                JSON_KEY_OMNIVOX_ID: current_id,
            }
        ] + new_teammates

        # Mettre à jour tous les coéquipiers sélectionnés
        for teammate in new_teammates:
            tm_id = self._teammate_id(teammate)
            if not tm_id or tm_id not in student_index:
                continue

            teammate_file = student_index[tm_id]
            try:
                with open(teammate_file, encoding="utf-8") as tf:
                    teammate_data = json.load(tf)

                teammate_data[JSON_KEY_TEAMMATES] = [
                    member for member in team_members if self._teammate_id(member) != tm_id
                ]

                with open(teammate_file, "w", encoding="utf-8") as tf:
                    json.dump(teammate_data, tf, ensure_ascii=False, indent=2)
            except Exception:
                continue

        # Nettoyer les anciens coéquipiers retirés
        removed_ids = old_ids - new_ids
        if removed_ids:
            for tm_id in removed_ids:
                if not tm_id or tm_id not in student_index:
                    continue

                teammate_file = student_index[tm_id]
                try:
                    with open(teammate_file, encoding="utf-8") as tf:
                        teammate_data = json.load(tf)

                    existing = teammate_data.get(JSON_KEY_TEAMMATES, [])
                    filtered = [tm for tm in existing if self._teammate_id(tm) not in team_ids]
                    teammate_data[JSON_KEY_TEAMMATES] = filtered

                    with open(teammate_file, "w", encoding="utf-8") as tf:
                        json.dump(teammate_data, tf, ensure_ascii=False, indent=2)
                except Exception:
                    continue
