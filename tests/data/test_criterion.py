"""Tests for c3hm.data.criterion module."""

import pytest

from c3hm.data.criterion import Criterion
from c3hm.data.indicator import Indicator


class TestCriterion:
    """Tests for Criterion class."""

    def test_criterion_initialization(self):
        """Test Criterion object initialization."""
        indicators = [
            Indicator(label="Indicator 1", points=5, descriptors=["Desc1"]),
            Indicator(label="Indicator 2", points=5, descriptors=["Desc2"]),
        ]
        criterion = Criterion(label="Test Criterion", indicators=indicators, grade_override=None)
        assert criterion.label == "Test Criterion"
        assert criterion.indicators == indicators
        assert criterion.grade_override is None

    def test_criterion_initialization_with_grade_override(self):
        """Test Criterion initialization with grade override."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=7.5)
        assert criterion.grade_override == 7.5

    def test_points(self):
        """Test points calculation."""
        indicators = [
            Indicator(label="Ind1", points=10, descriptors=["D"]),
            Indicator(label="Ind2", points=15, descriptors=["D"]),
            Indicator(label="Ind3", points=25, descriptors=["D"]),
        ]
        criterion = Criterion(label="Test", indicators=indicators)
        assert criterion.points() == 50

    def test_points_single_indicator(self):
        """Test points with single indicator."""
        indicators = [Indicator(label="Ind", points=7.5, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators)
        assert criterion.points() == 7.5

    def test_points_zero_points_indicator(self):
        """Test points with indicator having zero points."""
        indicators = [
            Indicator(label="Ind1", points=10, descriptors=["D"]),
            Indicator(label="Ind2", points=0, descriptors=["D"]),
        ]
        criterion = Criterion(label="Test", indicators=indicators)
        assert criterion.points() == 10

    def test_validate_valid_criterion(self):
        """Test validation of valid criterion."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Valid", indicators=indicators)
        # Should not raise
        criterion.validate()

    def test_validate_empty_label_raises_error(self):
        """Test that empty label raises ValueError."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="", indicators=indicators)
        with pytest.raises(ValueError, match=r"Le champ 'critère' doit être une chaîne de caractères non vide\."):
            criterion.validate()

    def test_validate_none_label_raises_error(self):
        """Test that None label raises ValueError."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label=None, indicators=indicators)  # type: ignore
        with pytest.raises(ValueError, match=r"Le champ 'critère' doit être une chaîne de caractères non vide\."):
            criterion.validate()

    def test_validate_empty_indicators_raises_error(self):
        """Test that empty indicators list raises ValueError."""
        criterion = Criterion(label="Test", indicators=[])
        with pytest.raises(ValueError, match=r"Le critère 'Test' doit contenir une liste d'indicateurs non vide\."):
            criterion.validate()

    def test_validate_non_list_indicators_raises_error(self):
        """Test that non-list indicators raises ValueError."""
        criterion = Criterion(label="Test", indicators="not a list")  # type: ignore
        with pytest.raises(ValueError, match=r"Le critère 'Test' doit contenir une liste d'indicateurs non vide\."):
            criterion.validate()

    def test_validate_invalid_indicator_raises_error(self):
        """Test that invalid indicator in list raises ValueError."""
        indicators = [Indicator(label="", points=10, descriptors=["D"])]  # Empty label is invalid
        criterion = Criterion(label="Test", indicators=indicators)
        with pytest.raises(ValueError):
            criterion.validate()

    def test_validate_grade_override_type_raises_error(self):
        """Test that non-numeric grade override raises ValueError."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators, grade_override="invalid")  # type: ignore
        with pytest.raises(ValueError, match=r"La note du critère 'Test' doit être un nombre\."):
            criterion.validate()

    def test_validate_grade_override_negative_raises_error(self):
        """Test that negative grade override raises ValueError."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=-1)
        with pytest.raises(ValueError, match=r"La note du critère 'Test' doit être entre 0 et 10 points\."):
            criterion.validate()

    def test_validate_grade_override_exceeds_max_raises_error(self):
        """Test that grade override exceeding max points raises ValueError."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=11)
        with pytest.raises(ValueError, match=r"La note du critère 'Test' doit être entre 0 et 10 points\."):
            criterion.validate()

    def test_validate_grade_override_zero_is_valid(self):
        """Test that grade override of zero is valid."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=0)
        # Should not raise
        criterion.validate()

    def test_validate_grade_override_at_max_is_valid(self):
        """Test that grade override at maximum points is valid."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=10)
        # Should not raise
        criterion.validate()

    def test_to_dict_without_override(self, sample_indicator):
        """Test serialization without grade override."""
        indicators = [sample_indicator]
        criterion = Criterion(label="Test", indicators=indicators)
        data = criterion.to_dict(include_graded_level=False)
        assert data["critère"] == "Test"
        assert "note ajustée" not in data
        assert "indicateurs" in data

    def test_to_dict_with_override(self, sample_indicator):
        """Test serialization with grade override."""
        indicators = [sample_indicator]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=5.5)
        data = criterion.to_dict(include_graded_level=True)
        assert data["critère"] == "Test"
        assert data["note ajustée"] == 5.5

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "critère": "Test Criterion",
            "indicateurs": [
                {"indicateur": "Ind1", "points": 5, "descripteurs": ["D1"]},
                {"indicateur": "Ind2", "points": 5, "descripteurs": ["D2"]},
            ],
        }
        criterion = Criterion.from_dict(data)
        assert criterion.label == "Test Criterion"
        assert len(criterion.indicators) == 2
        assert criterion.grade_override is None

    def test_from_dict_with_override(self):
        """Test deserialization with grade override."""
        data = {
            "critère": "Test",
            "note ajustée": 7.5,
            "indicateurs": [{"indicateur": "Ind", "points": 10, "descripteurs": ["D"]}],
        }
        criterion = Criterion.from_dict(data)
        assert criterion.label == "Test"
        assert criterion.grade_override == 7.5

    def test_copy(self):
        """Test that copy creates a deep copy."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"])]
        original = Criterion(label="Test", indicators=indicators, grade_override=5)
        copied = original.copy()

        # Check values are equal
        assert copied.label == original.label
        assert len(copied.indicators) == len(original.indicators)
        assert copied.grade_override == original.grade_override

        # Modify copy
        copied.label = "Modified"
        copied.grade_override = 8

        # Original should be unchanged
        assert original.label == "Test"
        assert original.grade_override == 5

    def test_grade_returns_override_if_set(self, mock_grid):
        """Test that grade returns override if set."""
        indicators = [Indicator(label="Ind", points=10, descriptors=["D"], graded_level="Bien maîtrisé")]
        criterion = Criterion(label="Test", indicators=indicators, grade_override=3.5)
        assert criterion.grade(mock_grid) == 3.5

    def test_grade_sums_indicator_grades(self, mock_grid):
        """Test that grade sums indicator grades."""
        indicators = [
            Indicator(label="Ind1", points=10, descriptors=["D"], graded_level="Bien maîtrisé"),
            Indicator(label="Ind2", points=20, descriptors=["D"], graded_level="Acquis"),
        ]
        criterion = Criterion(label="Test", indicators=indicators)
        # 10*1.0 + 20*0.75 = 10 + 15 = 25
        assert criterion.grade(mock_grid) == 25


class TestCriterionWithFixtures:
    """Tests using fixtures."""

    def test_sample_indicator_in_criterion(self, sample_indicator):
        """Test using sample_indicator fixture in criterion."""
        criterion = Criterion(label="Test", indicators=[sample_indicator])
        assert criterion.points() == 10
        assert len(criterion.indicators) == 1
