from decimal import Decimal

import pytest
from pydantic_core import ValidationError

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.indicator import Indicator


def make_indicator(id="ind1", grade: Decimal | None =Decimal("2"), points=Decimal("2")):
    # Minimal Indicator mock for testing
    return Indicator(
        id=id,
        description="Test Indicator",
        grade=grade,
        points=points,
        comment="Test comment" if grade is not None else ""
        )

def test_criterion_has_grade_with_override():
    indicators = [make_indicator()]
    c = Criterion(id="crit1", name="Critère 1", indicators=indicators, override_grade=Decimal("1"),
                  comment="Test")
    assert c.has_grade is True
    assert c.has_override is True
    assert c.get_grade() == Decimal("1")

def test_criterion_has_grade_without_override():
    indicators = [make_indicator()]
    c = Criterion(id="crit2", name="Critère 2", indicators=indicators, override_grade=None,
                  comment="Test")
    assert c.has_grade is True
    assert c.has_override is False
    assert c.get_grade() == Decimal("2")


def test_criterion_get_grade_raises_when_no_grade():
    indicators = [make_indicator(grade=None)]
    c = Criterion(id="crit7", name="Critère 7", indicators=indicators, override_grade=None,
                  comment="")
    with pytest.raises(ValueError):
        c.get_grade()

def test_criterion_points_property():
    indicators = [make_indicator(points=Decimal("2")),
                  make_indicator(id="ind2", points=Decimal("3"))]
    c = Criterion(id="crit8", name="Critère 8", indicators=indicators, override_grade=None,
                  comment="Test")
    assert c.points == Decimal("5")

def test_criterion_nb_indicators():
    indicators = [make_indicator(), make_indicator(id="ind2")]
    c = Criterion(id="crit9", name="Critère 9", indicators=indicators, override_grade=None,
                  comment="Test")
    assert c.nb_indicators == 2

def test_criterion_to_dict_and_from_dict():
    indicators = [make_indicator(), make_indicator(id="ind2")]
    c = Criterion(id="crit10", name="Critère 10", indicators=indicators,
                  override_grade=Decimal("4"),
                  comment="Test comment")
    d = c.to_dict(convert_decimal=True)
    c2 = Criterion.from_dict(d)
    assert c2.id == c.id
    assert c2.name == c.name
    assert len(c2.indicators) == 2
    assert c2.override_grade == c.override_grade
    assert c2.comment == c.comment

def test_criterion_copy():
    indicators = [make_indicator(), make_indicator(id="ind2")]
    c = Criterion(id="crit11", name="Critère 11", indicators=indicators,
                  override_grade=Decimal("4"),
                  comment="Test comment")
    c2 = c.copy()
    assert c2 is not c
    assert c2.id == c.id
    assert c2.name == c.name
    assert c2.override_grade == c.override_grade
    assert c2.comment == c.comment
    assert all(i1.id == i2.id for i1, i2 in zip(c.indicators, c2.indicators, strict=True))
    assert all(i1 is not i2 for i1, i2 in zip(c.indicators, c2.indicators, strict=True))

def test_criterion_duplicate_indicator_ids_raises():
    indicators = [make_indicator(id="dup"), make_indicator(id="dup")]
    with pytest.raises(ValueError):
        Criterion(id="crit12", name="Critère 12", indicators=indicators, override_grade=None,
                  comment="Test")

def test_criterion_invalid_excel_id_raises():
    indicators = [make_indicator()]
    with pytest.raises(ValueError):
        Criterion(id="123", name="Critère 13", indicators=indicators,
                  override_grade=None,
                  comment="Test")

def test_criterion_override_grade_greater_than_points_raises():
    indicators = [make_indicator(points=Decimal("2"))]
    with pytest.raises(ValueError):
        Criterion(id="crit14", name="Critère 14", indicators=indicators,
                  override_grade=Decimal("5"),
                  comment="Test")

def test_criterion_override_grade_requires_all_indicators_graded():
    indicators = [make_indicator(grade=None)]
    with pytest.raises(ValidationError):
        Criterion(id="crit15", name="Critère 15", indicators=indicators,
                  override_grade=Decimal("1"),
                  comment="Test")

def test_criterion_partial_indicators_graded_raises():
    indicators = [make_indicator(), make_indicator(id="ind2", grade=None)]
    with pytest.raises(ValidationError):
        Criterion(id="crit16", name="Critère 16", indicators=indicators, override_grade=None,
                  comment="Test")

def test_criterion_comment_is_stripped():
    indicators = [make_indicator()]
    c = Criterion(id="crit17", name="Critère 17", indicators=indicators, override_grade=None,
                  comment="   Test comment   ")
    assert c.comment == "Test comment"

