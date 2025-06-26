from decimal import Decimal

import pytest

from c3hm.data.rubric.grade import Grade


def test_grade_creation():
    g = Grade(value=Decimal("2.5"), comment="Good job")
    assert g.value == Decimal("2.5")
    assert g.comment == "Good job"

def test_grade_comment_strip():
    g = Grade(value=Decimal("1.0"), comment="  Needs improvement  ")
    assert g.comment == "Needs improvement"

def test_has_comment_true():
    g = Grade(value=Decimal("1.0"), comment="Some comment")
    assert g.has_comment is True

def test_has_comment_false():
    g = Grade(value=Decimal("1.0"), comment="   ")
    assert g.has_comment is False

def test_to_dict_without_decimal_conversion():
    g = Grade(value=Decimal("3.5"), comment="Nice")
    d = g.to_dict()
    assert d == {"value": Decimal("3.5"), "comment": "Nice"}

def test_to_dict_with_decimal_conversion():
    g = Grade(value=Decimal("4.25"), comment="Well done")
    d = g.to_dict(convert_decimal=True)
    assert d["value"] == 4.25
    assert d["comment"] == "Well done"

def test_from_dict():
    data = {"value": Decimal("2.0"), "comment": "Ok"}
    g = Grade.from_dict(data)
    assert g.value == Decimal("2.0")
    assert g.comment == "Ok"

def test_copy():
    g1 = Grade(value=Decimal("5.0"), comment="Excellent")
    g2 = g1.copy()
    assert g1 is not g2
    assert g1.value == g2.value
    assert g1.comment == g2.comment

def test_value_must_be_non_negative():
    with pytest.raises(ValueError):
        Grade(value=Decimal("-1.0"), comment="Negative")
