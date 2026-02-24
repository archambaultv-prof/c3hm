"""Tests for c3hm.data.grid module."""

import pytest

from c3hm.data.criterion import Criterion
from c3hm.data.grid import Grid
from c3hm.data.indicator import Indicator
from c3hm.data.level import DEFAULT_LEVELS


class TestGrid:
    """Tests for Grid class."""

    def test_grid_initialization(self):
        """Test Grid initialization."""
        criteria = [
            Criterion(
                label="Criterion 1",
                indicators=[Indicator(label="Ind", points=50, descriptors=["D"] * 5)],
            ),
            Criterion(
                label="Criterion 2",
                indicators=[Indicator(label="Ind", points=50, descriptors=["D"] * 5)],
            ),
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert len(grid.criteria) == 2
        assert len(grid.levels) == 5
        assert grid.show_criteria_points is True
        assert grid.show_levels_percentage is True

    def test_grid_initialization_without_custom_levels(self):
        """Test Grid initialization uses DEFAULT_LEVELS if not provided."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria)
        assert len(grid.levels) == 5
        assert grid.levels == DEFAULT_LEVELS

    def test_validate_empty_criteria_raises_error(self):
        """Test that empty criteria raises ValueError."""
        grid = Grid(criteria=[])
        with pytest.raises(ValueError, match=r"La grille doit contenir une liste de critères non vide\."):
            grid.validate()

    def test_validate_criteria_points_not_100_raises_error(self):
        """Test that criteria points not summing to 100 raises ValueError."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=99, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria)
        with pytest.raises(ValueError, match=r"La somme totale des points.*doit être égale à 100"):
            grid.validate()

    def test_validate_criteria_points_exceeds_100_raises_error(self):
        """Test that criteria points exceeding 100 raises ValueError."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=101, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria)
        with pytest.raises(ValueError, match=r"La somme totale des points.*doit être égale à 100"):
            grid.validate()

    def test_validate_criteria_points_exactly_100(self):
        """Test that criteria points exactly 100 passes validation."""
        criteria = [
            Criterion(
                label="Crit1",
                indicators=[Indicator(label="Ind", points=50, descriptors=["D"] * 5)],
            ),
            Criterion(
                label="Crit2",
                indicators=[Indicator(label="Ind", points=50, descriptors=["D"] * 5)],
            ),
        ]
        grid = Grid(criteria=criteria)
        # Should not raise
        grid.validate()

    def test_validate_descriptor_count_mismatch_raises_error(self):
        """Test that descriptor count not matching level count raises error."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D1", "D2"])],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        with pytest.raises(ValueError, match=r"L'indicateur.*doit contenir une liste de descripteurs de longueur"):
            grid.validate()

    def test_validate_graded_level_unknown_raises_error(self):
        """Test that unknown graded level raises error."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[
                    Indicator(
                        label="Ind",
                        points=100,
                        descriptors=["D"] * 5,
                        graded_level="Unknown Level",
                    )
                ],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        with pytest.raises(ValueError, match=r"Niveau noté inconnu"):
            grid.validate()

    def test_level_to_percentage(self):
        """Test level_to_percentage conversion."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert grid.level_to_percentage("Bien maîtrisé") == 1.0
        assert grid.level_to_percentage("Acquis") == 0.75
        assert grid.level_to_percentage("Ça y est presque!") == 0.5
        assert grid.level_to_percentage("En apprentissage") == 0.25
        assert grid.level_to_percentage("Non démontré") == 0.0

    def test_level_to_percentage_case_insensitive(self):
        """Test level_to_percentage is case-insensitive."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert grid.level_to_percentage("bien maîtrisé") == 1.0
        assert grid.level_to_percentage("ACQUIS") == 0.75

    def test_level_to_percentage_accent_insensitive(self):
        """Test level_to_percentage normalizes accents."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert grid.level_to_percentage("Bien maitrise") == 1.0
        assert grid.level_to_percentage("Ça y est presque!") == 0.5

    def test_level_to_percentage_unknown_raises_error(self):
        """Test that unknown level raises ValueError."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        with pytest.raises(ValueError, match=r"Niveau de performance inconnu"):
            grid.level_to_percentage("Unknown")

    def test_level_to_rank(self):
        """Test level_to_rank conversion."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert grid.level_to_rank("Bien maîtrisé") == 0
        assert grid.level_to_rank("Acquis") == 1
        assert grid.level_to_rank("Ça y est presque!") == 2
        assert grid.level_to_rank("En apprentissage") == 3
        assert grid.level_to_rank("Non démontré") == 4

    def test_is_graded_all_graded(self):
        """Test is_graded returns True when all indicators are graded."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[
                    Indicator(
                        label="Ind",
                        points=100,
                        descriptors=["D"] * 5,
                        graded_level="Bien maîtrisé",
                    )
                ],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert grid.is_graded() is True

    def test_is_graded_not_all_graded(self):
        """Test is_graded returns False when not all indicators are graded."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],  # No graded_level
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        assert grid.is_graded() is False

    def test_grade_single_criterion(self):
        """Test grade calculation with single criterion."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[
                    Indicator(
                        label="Ind",
                        points=100,
                        descriptors=["D"] * 5,
                        graded_level="Bien maîtrisé",
                    )
                ],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        # 100 * 1.0 = 100
        assert grid.grade() == 100

    def test_grade_multiple_criteria_with_rounding(self):
        """Test grade calculation with rounding."""
        criteria = [
            Criterion(
                label="Crit1",
                indicators=[
                    Indicator(
                        label="Ind",
                        points=33.33,
                        descriptors=["D"] * 5,
                        graded_level="Acquis",
                    )
                ],
            ),
            Criterion(
                label="Crit2",
                indicators=[
                    Indicator(
                        label="Ind",
                        points=33.33,
                        descriptors=["D"] * 5,
                        graded_level="Ça y est presque!",
                    )
                ],
            ),
            Criterion(
                label="Crit3",
                indicators=[
                    Indicator(
                        label="Ind",
                        points=33.34,
                        descriptors=["D"] * 5,
                        graded_level="En apprentissage",
                    )
                ],
            ),
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        grade = grid.grade()
        assert isinstance(grade, float)

    def test_copy(self):
        """Test that copy creates a deep copy."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        original = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        copied = original.copy()

        assert len(copied.criteria) == len(original.criteria)
        assert len(copied.levels) == len(original.levels)

        # Modify copy
        copied.criteria[0].label = "Modified"

        # Original should be unchanged
        assert original.criteria[0].label == "Criterion"

    def test_to_dict_basic(self):
        """Test serialization to dict."""
        criteria = [
            Criterion(
                label="Criterion",
                indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
            )
        ]
        grid = Grid(criteria=criteria, levels=DEFAULT_LEVELS)
        data = grid.to_dict()
        assert "niveaux" in data
        assert "critères" in data
        assert len(data["niveaux"]) == 5
        assert len(data["critères"]) == 1

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "afficher les points des critères": True,
            "afficher les pourcentages des niveaux": False,
            "niveaux": [
                {"niveau": "Excellent", "pourcentage": 1.0, "abréviations": ["e"]},
                {"niveau": "Good", "pourcentage": 0.5},
            ],
            "critères": [
                {
                    "critère": "Test Criterion",
                    "indicateurs": [
                        {"indicateur": "Indicator 1", "points": 50, "descripteurs": ["D"] * 2},
                        {"indicateur": "Indicator 2", "points": 50, "descripteurs": ["D"] * 2},
                    ],
                }
            ],
        }
        grid = Grid.from_dict(data)
        assert len(grid.criteria) == 1
        assert len(grid.levels) == 2
        assert grid.show_criteria_points is True
        assert grid.show_levels_percentage is False
