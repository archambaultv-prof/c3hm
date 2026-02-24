"""Tests for c3hm.data.indicator module."""

import pytest

from c3hm.data.indicator import Indicator


class TestIndicator:
    """Tests for Indicator class."""

    def test_indicator_initialization(self):
        """Test Indicator object initialization."""
        indicator = Indicator(
            label="Clarté du code",
            points=10,
            descriptors=["Code bien structuré", "Variables explicites"],
            graded_level="Excellent",
        )
        assert indicator.label == "Clarté du code"
        assert indicator.points == 10
        assert indicator.descriptors == ["Code bien structuré", "Variables explicites"]
        assert indicator.graded_level == "Excellent"

    def test_indicator_initialization_without_graded_level(self):
        """Test Indicator initialization without graded_level."""
        indicator = Indicator(label="Test", points=5, descriptors=["Desc1"])
        assert indicator.label == "Test"
        assert indicator.points == 5
        assert indicator.descriptors == ["Desc1"]
        assert indicator.graded_level is None

    def test_validate_valid_indicator(self):
        """Test validation of a valid Indicator."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc1", "Desc2"], graded_level="Bon")
        # Should not raise any exception
        indicator.validate()

    def test_validate_valid_indicator_without_graded_level(self):
        """Test validation of indicator without graded_level."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc1"])
        # Should not raise any exception
        indicator.validate()

    def test_validate_empty_label_raises_error(self):
        """Test that empty label raises ValueError."""
        indicator = Indicator(label="", points=10, descriptors=["Desc"])
        with pytest.raises(ValueError, match=r"Le champ 'indicateur' doit être une chaîne de caractères non vide\."):
            indicator.validate()

    def test_validate_none_label_raises_error(self):
        """Test that None label raises ValueError."""
        indicator = Indicator(label=None, points=10, descriptors=["Desc"])  # type: ignore
        with pytest.raises(ValueError, match=r"Le champ 'indicateur' doit être une chaîne de caractères non vide\."):
            indicator.validate()

    def test_validate_empty_graded_level_raises_error(self):
        """Test that empty graded_level raises ValueError."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level="")
        with pytest.raises(ValueError, match=r"Le champ 'niveau noté' doit être une chaîne de caractères non vide\."):
            indicator.validate()

    def test_validate_negative_points_raises_error(self):
        """Test that negative points raise ValueError."""
        indicator = Indicator(label="Test", points=-5, descriptors=["Desc"])
        with pytest.raises(ValueError, match=r"Le champ 'points' de l'indicateur 'Test' doit être un nombre positif\."):
            indicator.validate()

    def test_validate_zero_points_is_valid(self):
        """Test that zero points is valid."""
        indicator = Indicator(label="Test", points=0, descriptors=["Desc"])
        # Should not raise any exception
        indicator.validate()

    def test_validate_invalid_points_type_raises_error(self):
        """Test that invalid points type raises ValueError."""
        indicator = Indicator(label="Test", points="invalid", descriptors=["Desc"])  # type: ignore
        with pytest.raises(ValueError, match=r"Le champ 'points' de l'indicateur 'Test' doit être un nombre positif\."):
            indicator.validate()

    def test_validate_empty_descriptor_raises_error(self):
        """Test that empty descriptors raise ValueError."""
        indicator = Indicator(label="Test", points=10, descriptors=["Valid", "", "Another"])
        with pytest.raises(ValueError, match=r"Le champ 'descripteur' doit être une chaîne de caractères non vide\."):
            indicator.validate()

    def test_validate_none_descriptor_raises_error(self):
        """Test that None in descriptors raises ValueError."""
        indicator = Indicator(label="Test", points=10, descriptors=["Valid", None])  # type: ignore
        with pytest.raises(ValueError, match=r"Le champ 'descripteur' doit être une chaîne de caractères non vide\."):
            indicator.validate()

    def test_to_dict_without_graded_level(self):
        """Test serialization to dict without graded_level."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc1", "Desc2"])
        data = indicator.to_dict(include_graded_level=False)
        assert data == {"indicateur": "Test", "points": 10, "descripteurs": ["Desc1", "Desc2"]}

    def test_to_dict_with_graded_level_not_included(self):
        """Test serialization to dict with graded_level but not included."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level="Bon")
        data = indicator.to_dict(include_graded_level=False)
        assert "niveau noté" not in data

    def test_to_dict_with_graded_level_included(self):
        """Test serialization to dict with graded_level included."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level="Excellent")
        data = indicator.to_dict(include_graded_level=True)
        assert data == {"indicateur": "Test", "points": 10, "descripteurs": ["Desc"], "niveau noté": "Excellent"}

    def test_to_dict_with_none_graded_level_included(self):
        """Test serialization with None graded_level when included."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level=None)
        data = indicator.to_dict(include_graded_level=True)
        assert data["niveau noté"] is None

    def test_from_dict_without_graded_level(self):
        """Test deserialization from dict without graded_level."""
        data = {"indicateur": "Test", "points": 10, "descripteurs": ["Desc1", "Desc2"]}
        indicator = Indicator.from_dict(data)
        assert indicator.label == "Test"
        assert indicator.points == 10
        assert indicator.descriptors == ["Desc1", "Desc2"]
        assert indicator.graded_level is None

    def test_from_dict_with_graded_level(self):
        """Test deserialization from dict with graded_level."""
        data = {"indicateur": "Test", "points": 10, "descripteurs": ["Desc"], "niveau noté": "Excellent"}
        indicator = Indicator.from_dict(data)
        assert indicator.label == "Test"
        assert indicator.points == 10
        assert indicator.descriptors == ["Desc"]
        assert indicator.graded_level == "Excellent"

    def test_from_dict_with_empty_graded_level(self):
        """Test that empty graded_level string is converted to None."""
        data = {"indicateur": "Test", "points": 10, "descripteurs": ["Desc"], "niveau noté": ""}
        indicator = Indicator.from_dict(data)
        assert indicator.graded_level is None

    def test_round_trip_serialization(self):
        """Test that Indicator survives round-trip serialization."""
        original = Indicator(label="Clarté", points=15, descriptors=["Clair", "Précis"], graded_level="Maîtrisé")
        data = original.to_dict(include_graded_level=True)
        restored = Indicator.from_dict(data)
        assert restored.label == original.label
        assert restored.points == original.points
        assert restored.descriptors == original.descriptors
        assert restored.graded_level == original.graded_level

    def test_copy(self):
        """Test that copy creates a deep copy."""
        original = Indicator(label="Test", points=10, descriptors=["Desc1", "Desc2"], graded_level="Bon")
        copied = original.copy()

        # Check values are equal
        assert copied.label == original.label
        assert copied.points == original.points
        assert copied.descriptors == original.descriptors
        assert copied.graded_level == original.graded_level

        # Modify the copy
        copied.label = "Modified"
        copied.points = 20
        copied.descriptors.append("Desc3")
        copied.graded_level = "Excellent"

        # Original should be unchanged
        assert original.label == "Test"
        assert original.points == 10
        assert original.descriptors == ["Desc1", "Desc2"]
        assert original.graded_level == "Bon"

    def test_grade_with_graded_level(self, mock_grid):
        """Test grade calculation with graded_level set."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level="Bien maîtrisé")
        grade = indicator.grade(mock_grid)
        # "Bien maîtrisé" has percentage 1.0 in DEFAULT_LEVELS
        assert grade == 10.0

    def test_grade_with_different_levels(self, mock_grid):
        """Test grade calculation with different graded levels."""
        indicator = Indicator(label="Test", points=20, descriptors=["Desc"], graded_level="Acquis")
        grade = indicator.grade(mock_grid)
        # "Acquis" has percentage 0.75
        assert grade == 15.0

        indicator.graded_level = "Ça y est presque!"
        grade = indicator.grade(mock_grid)
        # "Ça y est presque!" has percentage 0.5
        assert grade == 10.0

        indicator.graded_level = "En apprentissage"
        grade = indicator.grade(mock_grid)
        # "En apprentissage" has percentage 0.25
        assert grade == 5.0

        indicator.graded_level = "Non démontré"
        grade = indicator.grade(mock_grid)
        # "Non démontré" has percentage 0.0
        assert grade == 0.0

    def test_grade_without_graded_level_raises_error(self, mock_grid):
        """Test that grade without graded_level raises ValueError."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level=None)
        with pytest.raises(ValueError, match=r"Aucun niveau noté pour l'indicateur 'Test'\."):
            indicator.grade(mock_grid)

    def test_grade_with_short_label(self, mock_grid):
        """Test grade calculation using short labels."""
        indicator = Indicator(
            label="Test",
            points=10,
            descriptors=["Desc"],
            graded_level="m",  # Short label for "Bien maîtrisé"
        )
        grade = indicator.grade(mock_grid)
        assert grade == 10.0

    def test_grade_with_case_insensitive_level(self, mock_grid):
        """Test grade calculation with case-insensitive level matching."""
        indicator = Indicator(label="Test", points=10, descriptors=["Desc"], graded_level="ACQUIS")
        grade = indicator.grade(mock_grid)
        assert grade == 7.5

    def test_grade_with_accent_normalized_level(self, mock_grid):
        """Test grade calculation with accent normalization."""
        indicator = Indicator(
            label="Test",
            points=10,
            descriptors=["Desc"],
            graded_level="Bien maitrise",  # Without accent
        )
        grade = indicator.grade(mock_grid)
        assert grade == 10.0


class TestIndicatorWithFixtures:
    """Tests using fixtures from conftest.py."""

    def test_sample_indicator_fixture(self, sample_indicator):
        """Test that sample_indicator fixture is valid."""
        assert sample_indicator.label == "Clarté du code"
        assert sample_indicator.points == 10
        assert len(sample_indicator.descriptors) == 3
        assert sample_indicator.graded_level is None
        # Should pass validation
        sample_indicator.validate()
