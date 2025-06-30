import pytest
from pydantic_core import ValidationError

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.indicator import Indicator


def make_indicator(id="ind1", name="Indicateur 1", points=2.0):
    return Indicator(id=id, name=name, points=points)

def test_criterion_valid_creation():
    ind1 = make_indicator(id="ind1", name="Indicateur 1", points=2.5)
    ind2 = make_indicator(id="ind2", name="Indicateur 2", points=3.5)
    crit = Criterion(id="crit1", name="Critère 1", indicators=[ind1, ind2])
    assert crit.id == "crit1"
    assert crit.name == "Critère 1"
    assert len(crit.indicators) == 2
    assert crit.points == 6.0

def test_criterion_to_dict_and_from_dict():
    ind1 = make_indicator(id="ind1", name="Indicateur 1", points=1.0)
    crit = Criterion(id="crit1", name="Critère 1", indicators=[ind1])
    d = crit.to_dict()
    assert d["id"] == "crit1"
    assert d["critère"] == "Critère 1"
    assert isinstance(d["indicateurs"], list)
    crit2 = Criterion.from_dict(d)
    assert crit2.id == crit.id
    assert crit2.name == crit.name
    assert crit2.indicators[0].id == ind1.id

def test_criterion_copy():
    ind1 = make_indicator(id="ind1", name="Indicateur 1", points=2.0)
    crit = Criterion(id="crit1", name="Critère 1", indicators=[ind1])
    crit_copy = crit.copy()
    assert crit_copy is not crit
    assert crit_copy.id == crit.id
    assert crit_copy.indicators[0] is not crit.indicators[0]
    assert crit_copy.indicators[0].id == crit.indicators[0].id

def test_criterion_invalid_id_for_excel():
    ind1 = make_indicator()
    with pytest.raises(ValidationError) as exc:
        Criterion(id="invalid id!", name="Critère", indicators=[ind1])
    assert "n'est pas valide pour une cellule Excel" in str(exc.value)

def test_criterion_duplicate_indicator_ids():
    ind1 = make_indicator(id="dup")
    ind2 = make_indicator(id="dup")
    with pytest.raises(ValidationError) as exc:
        Criterion(id="crit1", name="Critère", indicators=[ind1, ind2])
    assert "doivent être uniques" in str(exc.value)

def test_criterion_empty_indicators():
    with pytest.raises(ValidationError):
        Criterion(id="crit1", name="Critère", indicators=[])

def test_criterion_min_length_id_and_name():
    ind1 = make_indicator()
    with pytest.raises(ValidationError):
        Criterion(id="", name="Critère", indicators=[ind1])
    with pytest.raises(ValidationError):
        Criterion(id="crit1", name="", indicators=[ind1])
