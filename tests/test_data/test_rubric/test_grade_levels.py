import pytest
from pydantic import ValidationError

from c3hm.data.rubric.grade_level import GradeLevel
from c3hm.data.rubric.grade_levels import GradeLevels


def make_levels():
    return [
        GradeLevel(name="Excellent", max_percentage=1.0, min_percentage=0.8),
        GradeLevel(name="Bon", max_percentage=0.75, min_percentage=0.5),
        GradeLevel(name="Insuffisant", max_percentage=0.45, min_percentage=0.0),
    ]


def test_grade_levels_valid_creation():
    levels = make_levels()
    gls = GradeLevels(levels=levels)
    assert gls.levels == levels


def test_grade_levels_invalid_order_raises():
    levels = [
        GradeLevel(name="Bon", max_percentage=0.75, min_percentage=0.5),
        GradeLevel(name="Excellent", max_percentage=1.0, min_percentage=0.8),
    ]
    with pytest.raises(ValidationError):
        GradeLevels(levels=levels)


def test_grade_levels_get_level_by_percentage():
    gls = GradeLevels(levels=make_levels())
    assert gls.get_level_by_percentage(0.9).name == "Excellent"
    assert gls.get_level_by_percentage(0.75).name == "Bon"
    assert gls.get_level_by_percentage(0.0).name == "Insuffisant"
    assert gls.get_level_by_percentage(0.5).name == "Bon"
    assert gls.get_level_by_percentage(0.8).name == "Excellent"


def test_grade_levels_get_level_by_percentage_out_of_bounds():
    gls = GradeLevels(levels=make_levels())
    with pytest.raises(ValueError):
        gls.get_level_by_percentage(-0.01)
    with pytest.raises(ValueError):
        gls.get_level_by_percentage(1.01)


def test_grade_levels_to_dict_and_from_dict():
    gls = GradeLevels(levels=make_levels())
    d = gls.to_dict()
    assert "niveaux" in d
    assert len(d["niveaux"]) == 3
    gls2 = GradeLevels.from_dict(d)
    assert gls2 == gls

def test_grade_levels_copy():
    gls = GradeLevels(levels=make_levels())
    gls_copy = gls.copy()
    assert gls_copy == gls
    assert gls_copy is not gls
    for l1, l2 in zip(gls.levels, gls_copy.levels, strict=True):
        assert l1 == l2
        assert l1 is not l2


def test_grade_levels_min_length():
    with pytest.raises(ValidationError):
        GradeLevels(levels=[])
        GradeLevels(levels=[])
