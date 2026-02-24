from c3hm.data import (
    JSON_KEY_CRITERIA,
    JSON_KEY_LEVELS,
    JSON_KEY_SHOW_CRITERIA_POINTS,
    JSON_KEY_SHOW_LEVELS_PERCENTAGE,
)
from c3hm.data.criterion import Criterion
from c3hm.data.level import DEFAULT_LEVELS, Level


class Grid:
    def __init__(
        self,
        criteria: list[Criterion],
        levels: list[Level] | None = None,
        show_criteria_points: bool = True,
        show_levels_percentage: bool = True,
    ):
        self.criteria = criteria
        self.levels = levels if levels is not None else DEFAULT_LEVELS
        self.show_criteria_points = show_criteria_points
        self.show_levels_percentage = show_levels_percentage

    def grade(self) -> float:
        return sum(round(criterion.grade(self), 0) for criterion in self.criteria)

    def copy(self) -> "Grid":
        new_levels = [level.copy() for level in self.levels] if self.levels is not None else None
        return Grid(
            criteria=[criterion.copy() for criterion in self.criteria],
            levels=new_levels,
            show_criteria_points=self.show_criteria_points,
            show_levels_percentage=self.show_levels_percentage,
        )

    def to_dict(self, include_graded_level: bool = False) -> dict:
        d = {
            JSON_KEY_SHOW_CRITERIA_POINTS: self.show_criteria_points,
            JSON_KEY_SHOW_LEVELS_PERCENTAGE: self.show_levels_percentage,
            JSON_KEY_LEVELS: [level.to_dict() for level in self.levels],
            JSON_KEY_CRITERIA: [criterion.to_dict(include_graded_level) for criterion in self.criteria],
        }
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Grid":
        criteria = [Criterion.from_dict(crit_data) for crit_data in data[JSON_KEY_CRITERIA]]
        levels = [Level.from_dict(level_data) for level_data in data[JSON_KEY_LEVELS]]
        show_criteria_points = data.get(JSON_KEY_SHOW_CRITERIA_POINTS, True)
        show_levels_percentage = data.get(JSON_KEY_SHOW_LEVELS_PERCENTAGE, True)
        return cls(
            criteria=criteria,
            levels=levels,
            show_criteria_points=show_criteria_points,
            show_levels_percentage=show_levels_percentage,
        )

    def level_to_percentage(self, level: str) -> float:
        if isinstance(level, str):
            for level_item in self.levels:
                if level_item.match_label(level):
                    return level_item.percentage
            else:
                raise ValueError(f"Niveau de performance inconnu: '{level}'")
        else:
            raise TypeError(f"Type de note inattendu: {type(level)}")

    def level_to_rank(self, level: str) -> int:
        if isinstance(level, str):
            for idx, level_item in enumerate(self.levels):
                if level_item.match_label(level):
                    return idx
            else:
                raise ValueError(f"Niveau de performance inconnu: '{level}'")
        else:
            raise TypeError(f"Type de note inattendu: {type(level)}")

    def validate(self) -> None:
        sum_points = 0.0
        if not self.criteria or not isinstance(self.criteria, list):
            raise ValueError("La grille doit contenir une liste de critères non vide.")
        for criterion in self.criteria:
            criterion.validate()
            sum_points += criterion.points()
        if sum_points != 100.0:
            raise ValueError(
                f"La somme totale des points des critères doit être égale à 100. Total trouvé: {sum_points}"
            )
        if not self.levels or not isinstance(self.levels, list):
            raise ValueError("La grille doit contenir une liste de niveaux non vide.")
        for level in self.levels:
            level.validate()
        nb_levels = len(self.levels)
        for criterion in self.criteria:
            for indicator in criterion.indicators:
                if indicator.descriptors is None or len(indicator.descriptors) != nb_levels:
                    raise ValueError(
                        f"L'indicateur '{indicator.label}' du critère '{criterion.label}' doit contenir une liste de "
                        f"descripteurs de longueur égale au nombre de niveaux ({nb_levels})."
                    )
                if indicator.graded_level is not None and not any(
                    level.match_label(indicator.graded_level) for level in self.levels
                ):
                    raise ValueError(
                        f"Niveau noté inconnu '{indicator.graded_level}' pour l'indicateur '{indicator.label}'."
                    )

    def is_graded(self) -> bool:
        """
        Vérifie si tous les indicateurs de la grille ont été notés.
        """
        for criterion in self.criteria:
            for indicator in criterion.indicators:
                if indicator.graded_level is None or indicator.graded_level.strip() == "":
                    return False
        return True
