from decimal import Decimal

import pytest

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.evaluation.indicator import Indicator


def make_indicator(id="ind1", grade: Decimal | None = Decimal("2"), points=Decimal("2")):
    return Indicator(
        id=id,
        description="Test Indicator",
        grade=grade,
        points=points,
        comment="Test comment" if grade is not None else ""
    )

def make_criterion(id="crit1", name="Critère 1", indicators=None, override_grade=None,
                   comment="Test"):
    if indicators is None:
        indicators = [make_indicator()]
    return Criterion(
        id=id,
        name=name,
        indicators=indicators,
        override_grade=override_grade,
        comment=comment
    )

def test_evaluation_title():
    criteria = [make_criterion()]
    e = Evaluation(
        name="Eval 1",
        grade_step=Decimal("1"),
        criteria=criteria,
        override_grade=None,
        comment="Test"
    )
    assert "Grille d'évaluation" in e.title()
    assert "Eval 1" in e.title()

def test_evaluation_points_property():
    criteria = [
        make_criterion(indicators=[make_indicator(points=Decimal("2"))]),
        make_criterion(id="crit2", indicators=[make_indicator(id="ind2", points=Decimal("3"))])
    ]
    e = Evaluation(
        name="Eval 2",
        grade_step=Decimal("1"),
        criteria=criteria,
        override_grade=None,
        comment="Test"
    )
    assert e.points == Decimal("5")
    assert e.nb_criteria == 2
    d = e.to_dict(convert_decimal=True)
    e2 = Evaluation.from_dict(d)
    assert e2.name == e.name
    assert e2.grade_step == e.grade_step
    assert len(e2.criteria) == 2
    assert e2.override_grade == e.override_grade
    assert e2.comment == e.comment

    e2 = e.copy()
    assert e2 is not e
    assert e2.name == e.name
    assert e2.grade_step == e.grade_step
    assert e2.override_grade == e.override_grade
    assert e2.comment == e.comment
    assert all(c1.id == c2.id for c1, c2 in zip(e.criteria, e2.criteria, strict=True))
    assert all(c1 is not c2 for c1, c2 in zip(e.criteria, e2.criteria, strict=True))


def test_evaluation_duplicate_criterion_ids_raises():
    criteria = [make_criterion(id="dup"), make_criterion(id="dup")]
    with pytest.raises(ValueError):
        Evaluation(
            name="Eval 6",
            grade_step=Decimal("1"),
            criteria=criteria,
            override_grade=None,
            comment="Test"
        )

def test_evaluation_override_grade_greater_than_points_raises():
    criteria = [make_criterion(indicators=[make_indicator(points=Decimal("2"))])]
    with pytest.raises(ValueError):
        Evaluation(
            name="Eval 7",
            grade_step=Decimal("1"),
            criteria=criteria,
            override_grade=Decimal("5"),
            comment="Test"
        )

def test_evaluation_override_grade_requires_all_criteria_graded():
    # One criterion has no grade
    indicators = [make_indicator(grade=None)]
    criteria = [make_criterion(indicators=indicators)]
    with pytest.raises(ValueError):
        Evaluation(
            name="Eval 8",
            grade_step=Decimal("1"),
            criteria=criteria,
            override_grade=Decimal("1"),
            comment="Test"
        )

def test_evaluation_indicator_points_not_multiple_of_grade_step_raises():
    indicators = [make_indicator(points=Decimal("1.5"), grade=None)]
    criteria = [make_criterion(indicators=indicators)]
    with pytest.raises(ValueError):
        Evaluation(
            name="Eval 9",
            grade_step=Decimal("1"),
            criteria=criteria,
            override_grade=None,
            comment="Test"
        )

def test_evaluation_comment_is_stripped():
    criteria = [make_criterion()]
    e = Evaluation(
        name="Eval 10",
        grade_step=Decimal("1"),
        criteria=criteria,
        override_grade=None,
        comment="   Test comment   "
    )
    assert e.comment == "Test comment"
