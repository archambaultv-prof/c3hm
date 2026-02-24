"""
Sérialisation des objets Rubric vers JSON pour l'API.
"""

from c3hm.data import (
    JSON_KEY_COMMENT,
    JSON_KEY_GRADE_OVERRIDE,
    JSON_KEY_GRADED_LEVEL,
)
from c3hm.data.level import get_colors
from c3hm.data.rubric import Rubric


class RubricSerializer:
    """
    Transforme un objet Rubric en dictionnaire JSON-safe pour les réponses API.

    Gère la conversion:
    - Des niveaux et couleurs
    - Des critères, indicateurs, et niveaux notés
    - Des overrides de notes
    - Des camarades et commentaires
    """

    @staticmethod
    def to_dict(rubric: Rubric, filename: str) -> dict:
        """
        Convertit une rubric en dictionnaire pour le front-end.

        Args:
            rubric: La rubric à convertir
            filename: Le nom du fichier

        Returns:
            Dictionnaire contenant les données pour l'affichage

        Raises:
            ValueError: Si la rubric n'a pas d'étudiant associé
        """
        if rubric.student is None:
            raise ValueError("Cette rubric n'a pas d'étudiant associé")

        student_name = f"{rubric.student.firstname} {rubric.student.surname}"

        level_colors = get_colors(len(rubric.grid.levels))
        levels = [
            {"label": level.label, "percentage": level.percentage, "color": level_colors[idx]}
            for idx, level in enumerate(rubric.grid.levels)
        ]

        criteria = []
        for _, criterion in enumerate(rubric.grid.criteria):
            indicators = []
            for _, indicator in enumerate(criterion.indicators):
                # Trouver l'index du niveau noté
                graded_level_idx = None
                if indicator.graded_level:
                    for level_idx, level in enumerate(rubric.grid.levels):
                        if level.match_label(indicator.graded_level):
                            graded_level_idx = level_idx
                            break

                indicators.append(
                    {
                        "label": indicator.label,
                        "points": indicator.points,
                        "descriptors": indicator.descriptors,
                        "graded_level": indicator.graded_level,
                        "graded_level_idx": graded_level_idx,
                    }
                )

            criteria.append(
                {"label": criterion.label, "grade_override": criterion.grade_override, "indicators": indicators}
            )

        return {
            "filename": filename,
            "student_name": student_name,
            "student": {
                "first_name": rubric.student.firstname,
                "last_name": rubric.student.surname,
                "omnivox_id": rubric.student.omnivox_id,
            },
            "levels": levels,
            "grade_override": rubric.grade_override,
            "criteria": criteria,
            "teammates": [
                {"first_name": tm.firstname, "last_name": tm.surname, "omnivox_id": tm.omnivox_id}
                for tm in rubric.teammates
            ],
            "comment": rubric.comment if rubric.comment is not None else "",
        }

    @staticmethod
    def copy_grid_comment_and_grade(source_data: dict, target_data: dict) -> None:
        """
        Copie la grille, le commentaire et les notes ajustées d'une rubric source
        vers une rubric cible.

        Utile pour la copie aux coéquipiers.

        Args:
            source_data: Dict JSON source
            target_data: Dict JSON cible (modifié in-place)
        """
        from c3hm.data import (
            JSON_KEY_CRITERIA,
            JSON_KEY_GRID,
            JSON_KEY_INDICATORS,
        )
        from c3hm.server.services.grade_manager import GradeManager

        source_grid = source_data.get(JSON_KEY_GRID, {})
        target_grid = target_data.get(JSON_KEY_GRID, {})
        source_criteria = source_grid.get(JSON_KEY_CRITERIA, [])
        target_criteria = target_grid.get(JSON_KEY_CRITERIA, [])

        # Copier les indicateurs et les overrides de critères
        for crit_idx, source_crit in enumerate(source_criteria):
            if crit_idx >= len(target_criteria):
                break

            # Copier l'override de note du critère
            source_override = GradeManager.get_criterion_override(source_crit)
            GradeManager.set_criterion_override(target_criteria[crit_idx], source_override)

            # Copier les niveaux notés des indicateurs
            source_indicators = source_crit.get(JSON_KEY_INDICATORS, [])
            target_indicators = target_criteria[crit_idx].get(JSON_KEY_INDICATORS, [])
            for ind_idx, source_ind in enumerate(source_indicators):
                if ind_idx >= len(target_indicators):
                    break
                target_indicators[ind_idx][JSON_KEY_GRADED_LEVEL] = source_ind.get(JSON_KEY_GRADED_LEVEL, "")

        # Copier le commentaire
        if JSON_KEY_COMMENT in source_data:
            target_data[JSON_KEY_COMMENT] = source_data.get(JSON_KEY_COMMENT, "")

        # Copier la note ajustée de la rubric
        if JSON_KEY_GRADE_OVERRIDE in source_data:
            target_data[JSON_KEY_GRADE_OVERRIDE] = source_data.get(JSON_KEY_GRADE_OVERRIDE)
