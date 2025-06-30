from decimal import Decimal

import pytest
from pydantic import ValidationError

from c3hm.data.rubric.grade_level import GradeLevel


def test_grade_level_valid_creation():
    gl = GradeLevel(
        name="Excellent",
        max_percentage=Decimal("0.20"),
        min_percentage=Decimal("0.16"),
    )
    assert gl.name == "Excellent"
    assert gl.max_percentage == Decimal("0.20")
    assert gl.min_percentage == Decimal("0.16")

def test_grade_level_minimum_equals_maximum():
    gl = GradeLevel(
        name="Unique",
        max_percentage=Decimal("0.10"),
        min_percentage=Decimal("0.10"),
    )
    assert gl.level_description() == "10%"

def test_grade_level_level_description_range():
    gl = GradeLevel(
        name="Passable",
        max_percentage=Decimal("0.15"),
        min_percentage=Decimal("0.10"),
    )
    assert gl.level_description() == "15% à 10%"

def test_grade_level_level_description_zero_minimum():
    gl = GradeLevel(
        name="Insuffisant",
        max_percentage=Decimal("0.09"),
        min_percentage=Decimal("0.0"),
    )
    assert gl.level_description() == "9% et moins"

def test_grade_level_to_dict_and_from_dict():
    gl = GradeLevel(
        name="Bon",
        max_percentage=Decimal("0.15"),
        min_percentage=Decimal("0.10"),
    )
    d = gl.to_dict()
    assert d["nom"] == "Bon"
    assert d["maximum"] == Decimal("0.15")
    assert d["minimum"] == Decimal("0.10")

    gl2 = GradeLevel.from_dict(d)
    assert gl2 == gl

def test_grade_level_copy():
    gl = GradeLevel(
        name="Bon",
        max_percentage=Decimal("0.15"),
        min_percentage=Decimal("0.10"),
    )
    gl_copy = gl.copy()
    assert gl_copy == gl
    assert gl_copy is not gl

def test_grade_level_name_min_length():
    with pytest.raises(ValidationError):
        GradeLevel(
            name="",
            max_percentage=Decimal("0.10"),
            min_percentage=Decimal("0.05"),
        )

def test_grade_level_minimum_greater_than_maximum():
    with pytest.raises(ValidationError):
        GradeLevel(
            name="Erreur",
            max_percentage=Decimal("0.10"),
            min_percentage=Decimal("0.12"),
        )
