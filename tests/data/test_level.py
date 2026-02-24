"""Tests for c3hm.data.level module."""

import pytest

from c3hm.data.level import DEFAULT_LEVELS, Level, get_colors


class TestGetColors:
    """Tests for get_colors function."""

    def test_get_colors_one_level(self):
        """Test color generation for 1 level."""
        colors = get_colors(1)
        assert len(colors) == 1
        assert colors[0] == "#C8FFC8"
        # Verify hex color format
        assert all(c.startswith("#") and len(c) == 7 for c in colors)

    def test_get_colors_two_levels(self):
        """Test color generation for 2 levels."""
        colors = get_colors(2)
        assert len(colors) == 2
        assert colors[0] == "#C8FFC8"
        assert colors[1] == "#FFE4C8"
        assert all(c.startswith("#") and len(c) == 7 for c in colors)

    def test_get_colors_three_levels(self):
        """Test color generation for 3 levels."""
        colors = get_colors(3)
        assert len(colors) == 3
        assert colors[0] == "#C8FFC8"
        assert colors[1] == "#F0FFB0"
        assert colors[2] == "#FFE4C8"
        assert all(c.startswith("#") and len(c) == 7 for c in colors)

    def test_get_colors_four_levels(self):
        """Test color generation for 4 levels."""
        colors = get_colors(4)
        assert len(colors) == 4
        assert all(c.startswith("#") and len(c) == 7 for c in colors)

    def test_get_colors_five_levels(self):
        """Test color generation for 5 levels (all base colors)."""
        colors = get_colors(5)
        assert len(colors) == 5
        expected = ["#C8FFC8", "#F0FFB0", "#FFF8C2", "#FFE4C8", "#FFC8C8"]
        assert colors == expected
        assert all(c.startswith("#") and len(c) == 7 for c in colors)

    def test_get_colors_zero_raises_error(self):
        """Test that requesting 0 levels raises ValueError."""
        with pytest.raises(ValueError, match=r"Le nombre de niveaux doit être au moins 1\."):
            get_colors(0)

    def test_get_colors_negative_raises_error(self):
        """Test that requesting negative levels raises ValueError."""
        with pytest.raises(ValueError, match=r"Le nombre de niveaux doit être au moins 1\."):
            get_colors(-1)

    def test_get_colors_six_raises_error(self):
        """Test that requesting more than 5 levels raises ValueError."""
        with pytest.raises(ValueError, match=r"Le nombre de niveaux ne peut pas dépasser 5\."):
            get_colors(6)

    def test_get_colors_large_number_raises_error(self):
        """Test that requesting many levels raises ValueError."""
        with pytest.raises(ValueError, match=r"Le nombre de niveaux ne peut pas dépasser 5\."):
            get_colors(10)


class TestLevel:
    """Tests for Level class."""

    def test_level_initialization(self):
        """Test Level object initialization."""
        level = Level(label="Excellent", percentage=1.0, short_label=["e", "ex"])
        assert level.label == "Excellent"
        assert level.percentage == 1.0
        assert level.short_label == ["e", "ex"]

    def test_level_initialization_without_short_label(self):
        """Test Level initialization without short_label."""
        level = Level(label="Bon", percentage=0.75)
        assert level.label == "Bon"
        assert level.percentage == 0.75
        assert level.short_label is None

    def test_match_label_exact(self):
        """Test exact label matching."""
        level = Level(label="Excellent", percentage=1.0)
        assert level.match_label("Excellent") is True

    def test_match_label_case_insensitive(self):
        """Test case-insensitive label matching."""
        level = Level(label="Excellent", percentage=1.0)
        assert level.match_label("excellent") is True
        assert level.match_label("EXCELLENT") is True
        assert level.match_label("ExCeLlEnT") is True

    def test_match_label_with_accents(self):
        """Test label matching with accent normalization."""
        level = Level(label="Maîtrisé", percentage=1.0)
        assert level.match_label("Maitrise") is True
        assert level.match_label("maîtrisé") is True
        assert level.match_label("MAITRISE") is True

        level2 = Level(label="Élève", percentage=0.5)
        assert level2.match_label("Eleve") is True
        assert level2.match_label("élève") is True

        level3 = Level(label="Ça va", percentage=0.5)
        assert level3.match_label("Ca va") is True
        assert level3.match_label("ça va") is True

    def test_match_label_with_whitespace(self):
        """Test label matching with leading/trailing whitespace."""
        level = Level(label="Excellent", percentage=1.0)
        assert level.match_label("  Excellent  ") is True
        assert level.match_label("\tExcellent\n") is True

    def test_match_label_with_short_labels(self):
        """Test matching with short labels."""
        level = Level(label="Bien maîtrisé", percentage=1.0, short_label=["m", "maîtrisé"])
        assert level.match_label("Bien maîtrisé") is True
        assert level.match_label("m") is True
        assert level.match_label("maîtrisé") is True
        assert level.match_label("M") is True  # case insensitive
        assert level.match_label("maitrise") is True  # accent normalization

    def test_match_label_no_match(self):
        """Test label matching with non-matching labels."""
        level = Level(label="Excellent", percentage=1.0)
        assert level.match_label("Bon") is False
        assert level.match_label("") is False
        assert level.match_label("Excel") is False

    def test_validate_valid_level(self):
        """Test validation of a valid Level."""
        level = Level(label="Bon", percentage=0.8, short_label=["b"])
        # Should not raise any exception
        level.validate()

    def test_validate_empty_label_raises_error(self):
        """Test that empty label raises ValueError."""
        level = Level(label="", percentage=0.5)
        with pytest.raises(ValueError, match=r"Le champ 'niveau' doit être une chaîne de caractères non vide\."):
            level.validate()

    def test_validate_invalid_percentage_type_raises_error(self):
        """Test that invalid percentage type raises ValueError."""
        level = Level(label="Test", percentage="invalid")  # type: ignore
        with pytest.raises(
            ValueError, match=r"Le champ 'pourcentage' du niveau 'Test' doit être un nombre entre 0 et 1\."
        ):
            level.validate()

    def test_validate_negative_percentage_raises_error(self):
        """Test that negative percentage raises ValueError."""
        level = Level(label="Test", percentage=-0.1)
        with pytest.raises(
            ValueError, match=r"Le champ 'pourcentage' du niveau 'Test' doit être un nombre entre 0 et 1\."
        ):
            level.validate()

    def test_validate_percentage_greater_than_one_raises_error(self):
        """Test that percentage > 1 raises ValueError."""
        level = Level(label="Test", percentage=1.5)
        with pytest.raises(
            ValueError, match=r"Le champ 'pourcentage' du niveau 'Test' doit être un nombre entre 0 et 1\."
        ):
            level.validate()

    def test_validate_invalid_short_label_type_raises_error(self):
        """Test that invalid short_label type raises ValueError."""
        level = Level(label="Test", percentage=0.5, short_label="not a list")  # type: ignore
        with pytest.raises(
            ValueError,
            match=r"Le champ 'abréviations' du niveau 'Test' doit être une liste de chaînes de caractères non vides\.",
        ):
            level.validate()

    def test_validate_empty_string_in_short_label_raises_error(self):
        """Test that empty strings in short_label raise ValueError."""
        level = Level(label="Test", percentage=0.5, short_label=["a", "", "c"])
        with pytest.raises(
            ValueError,
            match=r"Le champ 'abréviations' du niveau 'Test' doit être une liste de chaînes de caractères non vides\.",
        ):
            level.validate()

    def test_validate_non_string_in_short_label_raises_error(self):
        """Test that non-strings in short_label raise ValueError."""
        level = Level(label="Test", percentage=0.5, short_label=["a", 123, "c"])  # type: ignore
        with pytest.raises(
            ValueError,
            match=r"Le champ 'abréviations' du niveau 'Test' doit être une liste de chaînes de caractères non vides\.",
        ):
            level.validate()

    def test_to_dict_without_short_label(self):
        """Test serialization to dict without short_label."""
        level = Level(label="Bon", percentage=0.75)
        data = level.to_dict()
        assert data == {"niveau": "Bon", "pourcentage": 0.75}

    def test_to_dict_with_short_label(self):
        """Test serialization to dict with short_label."""
        level = Level(label="Excellent", percentage=1.0, short_label=["e", "ex"])
        data = level.to_dict()
        assert data == {"niveau": "Excellent", "pourcentage": 1.0, "abréviations": ["e", "ex"]}

    def test_from_dict_without_short_label(self):
        """Test deserialization from dict without short_label."""
        data = {"niveau": "Bon", "pourcentage": 0.75}
        level = Level.from_dict(data)
        assert level.label == "Bon"
        assert level.percentage == 0.75
        assert level.short_label is None

    def test_from_dict_with_short_label(self):
        """Test deserialization from dict with short_label."""
        data = {"niveau": "Excellent", "pourcentage": 1.0, "abréviations": ["e", "ex"]}
        level = Level.from_dict(data)
        assert level.label == "Excellent"
        assert level.percentage == 1.0
        assert level.short_label == ["e", "ex"]

    def test_round_trip_serialization(self):
        """Test that Level survives round-trip serialization."""
        original = Level(label="Maîtrisé", percentage=0.9, short_label=["m", "ok"])
        data = original.to_dict()
        restored = Level.from_dict(data)
        assert restored.label == original.label
        assert restored.percentage == original.percentage
        assert restored.short_label == original.short_label

    def test_copy(self):
        """Test that copy creates a deep copy."""
        original = Level(label="Test", percentage=0.5, short_label=["t", "test"])
        copied = original.copy()

        # Check values are equal
        assert copied.label == original.label
        assert copied.percentage == original.percentage
        assert copied.short_label == original.short_label

        # Modify the copy
        copied.label = "Modified"
        copied.percentage = 0.8
        copied.short_label.append("new")  # type: ignore

        # Original should be unchanged
        assert original.label == "Test"
        assert original.percentage == 0.5
        assert original.short_label == ["t", "test"]

    def test_copy_without_short_label(self):
        """Test copy when short_label is None."""
        original = Level(label="Test", percentage=0.5, short_label=None)
        copied = original.copy()

        assert copied.label == original.label
        assert copied.percentage == original.percentage
        assert copied.short_label is None


class TestDefaultLevels:
    """Tests for DEFAULT_LEVELS constant."""

    def test_default_levels_count(self):
        """Test that DEFAULT_LEVELS contains 5 levels."""
        assert len(DEFAULT_LEVELS) == 5

    def test_default_levels_have_colors(self):
        """Test that all default levels have valid structure."""
        for level in DEFAULT_LEVELS:
            assert isinstance(level, Level)
            assert isinstance(level.label, str)
            assert level.label != ""
            assert isinstance(level.percentage, float)
            assert 0 <= level.percentage <= 1
            assert isinstance(level.short_label, list)
            assert len(level.short_label) > 0

    def test_default_levels_percentages(self):
        """Test that default levels have correct percentages."""
        expected_percentages = [1.0, 0.75, 0.5, 0.25, 0.0]
        actual_percentages = [level.percentage for level in DEFAULT_LEVELS]
        assert actual_percentages == expected_percentages

    def test_default_levels_labels(self):
        """Test that default levels have expected labels."""
        expected_labels = ["Bien maîtrisé", "Acquis", "Ça y est presque!", "En apprentissage", "Non démontré"]
        actual_labels = [level.label for level in DEFAULT_LEVELS]
        assert actual_labels == expected_labels

    def test_default_levels_validate(self):
        """Test that all default levels pass validation."""
        for level in DEFAULT_LEVELS:
            # Should not raise any exception
            level.validate()
