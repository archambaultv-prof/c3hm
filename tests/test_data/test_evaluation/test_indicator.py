from decimal import Decimal

import pytest
from pydantic import ValidationError

from c3hm.data.evaluation.indicator import Indicator


def test_indicator_valid_with_grade():
    ind = Indicator(
        id="ind1",
        name="Test indicator",
        points=Decimal("10"),
        grade=Decimal("7"),
        comment=""
    )
    assert ind.id == "ind1"
    assert ind.name == "Test indicator"
    assert ind.points == Decimal("10")
    assert ind.grade == Decimal("7")
    assert ind.has_grade is True
    assert ind.comment == ""
    d = ind.to_dict()
    assert d["id"] == "ind1"
    assert d["indicateur"] == "Test indicator"
    assert d["points"] == Decimal("10")
    assert d["note"] == Decimal("7")
    assert d["commentaire"] == ""

def test_indicator_valid_without_grade():
    ind = Indicator(
        id="ind2",
        name="No grade",
        points=Decimal("5"),
        grade=None,
        comment=""
    )
    assert ind.has_grade is False
    assert ind.grade is None
    assert ind.comment == ""

def test_indicator_invalid_id_for_excel():
    # Patch safe_for_named_cell to return False
    with pytest.raises(ValidationError) as exc:
        Indicator(
            id="123",
            name="desc",
            points=Decimal("2"),
            grade=Decimal("1"),
            comment=""
        )
    assert "n'est pas valide pour une cellule Excel" in str(exc.value)

def test_indicator_grade_greater_than_points():
    with pytest.raises(ValidationError):
        Indicator(
            id="ind3",
            name="desc",
            points=Decimal("2"),
            grade=Decimal("3"),
            comment=""
        )

def test_indicator_comment_with_no_grade():
    with pytest.raises(ValidationError):
        Indicator(
            id="ind4",
            name="desc",
            points=Decimal("2"),
            grade=None,
            comment="Should not have comment"
        )

def test_indicator_comment_is_stripped():
    ind = Indicator(
        id="ind5",
        name="desc",
        points=Decimal("2"),
        grade=Decimal("2"),
        comment="   some comment   "
    )
    assert ind.comment == "some comment"

def test_indicator_to_dict_convert_decimal():
    ind = Indicator(
        id="ind6",
        name="desc",
        points=Decimal("2.5"),
        grade=Decimal("2"),
        comment=""
    )
    d = ind.to_dict(convert_decimal=True)
    assert isinstance(d["points"], float)
    assert isinstance(d["note"], int)

def test_indicator_from_dict_and_copy():
    data = {
        "id": "ind7",
        "indicateur": "desc",
        "points": Decimal("4"),
        "note": Decimal("3"),
        "commentaire": ""
    }
    ind = Indicator.from_dict(data)
    assert ind.id == "ind7"
    ind2 = ind.copy()
    assert ind2.id == ind.id
    assert ind2 is not ind
