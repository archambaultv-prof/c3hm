import pytest
from pydantic import ValidationError

from c3hm.data.evaluation.indicator import Indicator


def test_indicator_valid_creation():
    ind = Indicator(id="valid_id", name="Test Indicator", points=5.0)
    assert ind.id == "valid_id"
    assert ind.name == "Test Indicator"
    assert ind.points == 5.0

def test_indicator_invalid_id_empty():
    with pytest.raises(ValidationError):
        Indicator(id="", name="Test Indicator", points=5.0)

def test_indicator_invalid_points_zero():
    with pytest.raises(ValidationError):
        Indicator(id="valid_id", name="Test Indicator", points=0)

def test_indicator_invalid_points_negative():
    with pytest.raises(ValidationError):
        Indicator(id="valid_id", name="Test Indicator", points=-1)

def test_indicator_to_dict():
    ind = Indicator(id="valid_id", name="Test Indicator", points=3.5)
    d = ind.to_dict()
    assert d == {"id": "valid_id", "indicateur": "Test Indicator", "points": 3.5}

def test_indicator_from_dict():
    data = {"id": "valid_id", "indicateur": "Test Indicator", "points": 2.0}
    ind = Indicator.from_dict(data)
    assert ind.id == "valid_id"
    assert ind.name == "Test Indicator"
    assert ind.points == 2.0

def test_indicator_copy():
    ind = Indicator(id="valid_id", name="Test Indicator", points=1.0)
    ind_copy = ind.copy()
    assert ind_copy is not ind
    assert ind_copy.id == ind.id
    assert ind_copy.name == ind.name
    assert ind_copy.points == ind.points

def test_indicator_invalid_id_for_excel():
    # Assuming safe_for_named_cell does not allow spaces or special chars
    with pytest.raises(ValidationError):
        Indicator(id="invalid id!", name="Test Indicator", points=1.0)

    with pytest.raises(ValidationError):
        Indicator(id="123", name="Test Indicator", points=1.0)
