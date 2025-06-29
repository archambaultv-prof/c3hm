import pytest
from pydantic import ValidationError

from c3hm.data.rubric.descriptors import Descriptors


class DummyIndicator:
    def __init__(self, id):
        self.id = id

class DummyGradeLevel:
    def __init__(self, name):
        self.name = name

def make_sample():
    indicator = DummyIndicator("ind1")
    level = DummyGradeLevel("Excellent")
    descriptors = {("ind1", "Excellent"): "Description ABC"}
    return indicator, level, descriptors

def test_descriptors_valid_creation():
    _, _, descriptors_dict = make_sample()
    desc = Descriptors(descriptors=descriptors_dict)
    assert desc.descriptors == descriptors_dict

def test_descriptors_contains_true():
    indicator, level, descriptors_dict = make_sample()
    desc = Descriptors(descriptors=descriptors_dict)
    assert desc.contains(indicator, level) is True # type: ignore

def test_descriptors_contains_false():
    indicator, level, descriptors_dict = make_sample()
    desc = Descriptors(descriptors=descriptors_dict)
    other_indicator = DummyIndicator("ind2")
    other_level = DummyGradeLevel("Moyen")
    assert desc.contains(other_indicator, level) is False # type: ignore
    assert desc.contains(indicator, other_level) is False # type: ignore

def test_descriptors_get_descriptor_success():
    indicator, level, descriptors_dict = make_sample()
    desc = Descriptors(descriptors=descriptors_dict)
    assert desc.get_descriptor(indicator, level) == "Description ABC" # type: ignore

def test_descriptors_get_descriptor_key_error():
    _, level, descriptors_dict = make_sample()
    desc = Descriptors(descriptors=descriptors_dict)
    other_indicator = DummyIndicator("ind2")
    with pytest.raises(KeyError):
        desc.get_descriptor(other_indicator, level) # type: ignore

def test_descriptors_to_dict():
    _, _, descriptors_dict = make_sample()
    desc = Descriptors(descriptors=descriptors_dict)
    d = desc.to_dict()
    assert d == descriptors_dict

def test_descriptors_from_dict():
    _, _, descriptors_dict = make_sample()
    desc = Descriptors.from_dict(descriptors_dict)
    assert isinstance(desc, Descriptors)
    assert desc.descriptors == descriptors_dict

def test_descriptors_invalid_type():
    # descriptors must be a dict with tuple keys and str values
    with pytest.raises(ValidationError):
        Descriptors(descriptors={"not_a_tuple": 123}) # type: ignore
