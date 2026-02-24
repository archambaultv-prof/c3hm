"""Pytest fixtures for tests/data/."""

import pytest

from c3hm.data.indicator import Indicator
from c3hm.data.level import DEFAULT_LEVELS, Level


@pytest.fixture
def sample_levels():
    """Fixture providing DEFAULT_LEVELS for testing."""
    return DEFAULT_LEVELS


@pytest.fixture
def sample_level():
    """Fixture providing a single Level instance for testing."""
    return Level(label="Excellent", percentage=1.0, short_label=["e", "ex"])


@pytest.fixture
def sample_indicator():
    """Fixture providing a valid Indicator instance for testing."""
    return Indicator(
        label="Clarté du code",
        points=10,
        descriptors=[
            "Le code est bien structuré",
            "Les noms de variables sont explicites",
            "Les commentaires sont pertinents",
        ],
        graded_level=None,
    )


@pytest.fixture
def mock_grid():
    """Fixture providing a mock grid with level_to_percentage and level_to_rank methods."""

    class MockGrid:
        def __init__(self):
            self.levels = DEFAULT_LEVELS

        def level_to_percentage(self, level_label: str) -> float:
            """Convert a level label to its percentage value."""
            for level in self.levels:
                if level.match_label(level_label):
                    return level.percentage
            raise ValueError(f"Niveau inconnu: {level_label}")

        def level_to_rank(self, level_label: str) -> int:
            """Convert a level label to its rank (index in levels list)."""
            for i, level in enumerate(self.levels):
                if level.match_label(level_label):
                    return i
            raise ValueError(f"Niveau inconnu: {level_label}")

    return MockGrid()
