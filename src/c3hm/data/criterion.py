from typing import Any

from c3hm.data.indicator import HasLevelToPercentage, Indicator
from c3hm.data.utils import assert_non_empty_string


class Criterion:
    def __init__(self, label: str, indicators: list[Indicator], grade_override: float | None = None):
        self.label = label
        self.indicators = indicators
        self.grade_override = grade_override

    def grade(self, grid: HasLevelToPercentage) -> float:
        if self.grade_override is not None:
            return self.grade_override
        return sum(indicator.grade(grid) for indicator in self.indicators)

    def copy(self) -> "Criterion":
        return Criterion(
            label=self.label,
            indicators=[indicator.copy() for indicator in self.indicators],
            grade_override=self.grade_override,
        )

    def points(self) -> float:
        return sum(indicator.points for indicator in self.indicators)

    def to_dict(self, include_graded_level: bool = False) -> dict:
        d: dict[str, Any] = {
            "critère": self.label,
        }
        if include_graded_level:
            d["note ajustée"] = self.grade_override
        d["indicateurs"] = [indicator.to_dict(include_graded_level) for indicator in self.indicators]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        label = data["critère"]
        indicators = [Indicator.from_dict(ind_data) for ind_data in data["indicateurs"]]
        grade_override = data.get("note ajustée")
        return cls(label=label, indicators=indicators, grade_override=grade_override)

    def validate(self) -> None:
        assert_non_empty_string(self.label, field_name="critère")
        if not self.indicators or not isinstance(self.indicators, list):
            raise ValueError(f"Le critère '{self.label}' doit contenir une liste d'indicateurs non vide.")
        for indicator in self.indicators:
            indicator.validate()
        if self.grade_override is not None:
            if not isinstance(self.grade_override, int | float):
                raise ValueError(f"La note du critère '{self.label}' doit être un nombre.")
            if self.grade_override < 0 or self.grade_override > self.points():
                raise ValueError(f"La note du critère '{self.label}' doit être entre 0 et {self.points()} points.")
