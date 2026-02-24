"""Tests for c3hm.data.utils module."""

import pytest

from c3hm.data.utils import assert_non_empty_string


class TestAssertNonEmptyString:
    """Tests for assert_non_empty_string function."""

    def test_valid_string(self):
        """Test that valid non-empty strings pass without raising an error."""
        # Should not raise any exception
        assert_non_empty_string("hello", "test_field")
        assert_non_empty_string("a", "test_field")
        assert_non_empty_string("  text with spaces  ", "test_field")
        assert_non_empty_string("123", "test_field")
        assert_non_empty_string("éàçù", "test_field")

    def test_empty_string_raises_error(self):
        """Test that empty strings raise a ValueError."""
        with pytest.raises(ValueError, match=r"Le champ 'test_field' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string("", "test_field")

    def test_whitespace_only_raises_error(self):
        """Test that strings with only whitespace raise a ValueError."""
        with pytest.raises(ValueError, match=r"Le champ 'whitespace' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string("   ", "whitespace")

        with pytest.raises(ValueError, match=r"Le champ 'tabs' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string("\t\t", "tabs")

        with pytest.raises(ValueError, match=r"Le champ 'newlines' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string("\n\n", "newlines")

    def test_none_raises_error(self):
        """Test that None raises a ValueError."""
        with pytest.raises(ValueError, match=r"Le champ 'none_field' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string(None, "none_field")

    def test_non_string_types_raise_error(self):
        """Test that non-string types raise a ValueError."""
        # Test with integer
        with pytest.raises(ValueError, match=r"Le champ 'number' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string(123, "number")

        # Test with float
        with pytest.raises(ValueError, match=r"Le champ 'float' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string(3.14, "float")

        # Test with list
        with pytest.raises(ValueError, match=r"Le champ 'list' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string(["hello"], "list")

        # Test with dict
        with pytest.raises(ValueError, match=r"Le champ 'dict' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string({"key": "value"}, "dict")

        # Test with boolean
        with pytest.raises(ValueError, match=r"Le champ 'bool' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string(True, "bool")

    def test_field_name_in_error_message(self):
        """Test that the field name appears correctly in the error message."""
        with pytest.raises(ValueError, match=r"Le champ 'nom_etudiant' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string("", "nom_etudiant")

        with pytest.raises(ValueError, match=r"Le champ 'indicateur' doit être une chaîne de caractères non vide\."):
            assert_non_empty_string(None, "indicateur")
