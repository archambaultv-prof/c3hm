from decimal import Decimal

import pytest
from pydantic import ValidationError

from c3hm.data.rubric.grade_level import GradeLevel


def test_grade_level_valid_creation():
    gl = GradeLevel(
        name="Excellent",
        max_percentage=Decimal("20"),
        min_percentage=Decimal("16"),
        default_value=Decimal("18"),
    )
    assert gl.name == "Excellent"
    assert gl.max_percentage == Decimal("20")
    assert gl.min_percentage == Decimal("16")
    assert gl.default_value == Decimal("18")

def test_grade_level_invalid_default_value():
    with pytest.raises(ValidationError):
        GradeLevel(
            name="Bon",
            max_percentage=Decimal("15"),
            min_percentage=Decimal("10"),
            default_value=Decimal("16"),
        )

def test_grade_level_minimum_equals_maximum():
    gl = GradeLevel(
        name="Unique",
        max_percentage=Decimal("10"),
        min_percentage=Decimal("10"),
        default_value=Decimal("10"),
    )
    assert gl.level_description() == "10"

def test_grade_level_level_description_range():
    gl = GradeLevel(
        name="Passable",
        max_percentage=Decimal("15"),
        min_percentage=Decimal("10"),
        default_value=Decimal("12"),
    )
    assert gl.level_description() == "15 à 10"

def test_grade_level_level_description_zero_minimum():
    gl = GradeLevel(
        name="Insuffisant",
        max_percentage=Decimal("9"),
        min_percentage=Decimal("0"),
        default_value=Decimal("5"),
    )
    assert gl.level_description() == "9 et moins"

def test_grade_level_to_dict_and_from_dict():
    gl = GradeLevel(
        name="Bon",
        max_percentage=Decimal("15"),
        min_percentage=Decimal("10"),
        default_value=Decimal("12"),
    )
    d = gl.to_dict()
    assert d["nom"] == "Bon"
    assert d["maximum"] == Decimal("15")
    assert d["minimum"] == Decimal("10")
    assert d["valeur par défaut"] == Decimal("12")

    gl2 = GradeLevel.from_dict(d)
    assert gl2 == gl

def test_grade_level_to_dict_convert_decimal():
    gl = GradeLevel(
        name="Bon",
        max_percentage=Decimal("15.5"),
        min_percentage=Decimal("10.1"),
        default_value=Decimal("12.3"),
    )
    d = gl.to_dict(convert_decimal=True)
    assert isinstance(d["maximum"], float)
    assert isinstance(d["minimum"], float)
    assert isinstance(d["valeur par défaut"], float)

def test_grade_level_copy():
    gl = GradeLevel(
        name="Bon",
        max_percentage=Decimal("15"),
        min_percentage=Decimal("10"),
        default_value=Decimal("12"),
    )
    gl_copy = gl.copy()
    assert gl_copy == gl
    assert gl_copy is not gl

def test_grade_level_name_min_length():
    with pytest.raises(ValidationError):
        GradeLevel(
            name="",
            max_percentage=Decimal("10"),
            min_percentage=Decimal("5"),
            default_value=Decimal("7"),
        )

def test_grade_level_minimum_greater_than_maximum():
    with pytest.raises(ValidationError):
        GradeLevel(
            name="Erreur",
            max_percentage=Decimal("10"),
            min_percentage=Decimal("12"),
            default_value=Decimal("11"),
        )
