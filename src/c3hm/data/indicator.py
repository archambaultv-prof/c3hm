from typing import Protocol

from c3hm.data.utils import assert_non_empty_string


class HasLevelToPercentage(Protocol):
    def level_to_percentage(self, level) -> float: ...


class Indicator:
    def __init__(self, label: str, points: float, descriptors: list[str], graded_level: str | None = None):
        self.label = label
        self.points = points
        self.descriptors = descriptors
        self.graded_level = graded_level

    def copy(self) -> "Indicator":
        return Indicator(
            label=self.label, points=self.points, descriptors=self.descriptors.copy(), graded_level=self.graded_level
        )

    def validate(self) -> None:
        assert_non_empty_string(self.label, field_name="indicateur")
        if self.graded_level is not None:
            assert_non_empty_string(self.graded_level, field_name="niveau noté")
        if not isinstance(self.points, int | float) or self.points < 0:
            raise ValueError(f"Le champ 'points' de l'indicateur '{self.label}' doit être un nombre positif.")
        for desc in self.descriptors:
            assert_non_empty_string(desc, field_name="descripteur")

    def to_dict(self, include_graded_level: bool = False) -> dict:
        d = {"indicateur": self.label, "points": self.points, "descripteurs": self.descriptors}
        if include_graded_level:
            d["niveau noté"] = self.graded_level if self.graded_level else None
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Indicator":
        label = data["indicateur"]
        points = data["points"]
        descriptors = data["descripteurs"]
        graded_level = data.get("niveau noté")
        if graded_level == "":
            graded_level = None
        return cls(label=label, points=points, descriptors=descriptors, graded_level=graded_level)

    def grade(self, grid: HasLevelToPercentage) -> float:
        if self.graded_level is None:
            raise ValueError(f"Aucun niveau noté pour l'indicateur '{self.label}'.")
        return self.points * grid.level_to_percentage(self.graded_level)
