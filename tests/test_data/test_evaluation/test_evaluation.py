import pytest

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.evaluation.indicator import Indicator


def make_indicator(id_, points):
    return Indicator(id=id_, name=f"Indicator {id_}", points=points)

def make_criterion(id_, points, indicators=None):
    if indicators is None:
        indicators = [make_indicator(f"{id_}_ind1", points)]
    return Criterion(id=id_, name=f"Criterion {id_}", indicators=indicators)

def test_evaluation_title():
    crit = make_criterion("crit1", 5)
    eval_ = Evaluation(id="eval1", name="Test Eval", criteria=[crit])
    assert "Grille d'évaluation" in eval_.title()
    assert "Test Eval" in eval_.title()

def test_evaluation_points_sum():
    crit1 = make_criterion("crit1", 5)
    crit2 = make_criterion("crit2", 3)
    eval_ = Evaluation(id="eval2", name="Eval Points", criteria=[crit1, crit2])
    assert eval_.points == 8

def test_evaluation_to_dict_and_from_dict():
    crit = make_criterion("crit1", 4)
    eval_ = Evaluation(id="eval3", name="Eval Dict", criteria=[crit])
    d = eval_.to_dict()
    assert d["id"] == "eval3"
    assert d["nom"] == "Eval Dict"
    assert isinstance(d["critères"], list)
    eval2 = Evaluation.from_dict(d)
    assert eval2.id == eval_.id
    assert eval2.name == eval_.name
    assert eval2.criteria[0].id == crit.id

def test_evaluation_copy():
    crit = make_criterion("crit1", 2)
    eval_ = Evaluation(id="eval4", name="Eval Copy", criteria=[crit])
    eval2 = eval_.copy()
    assert eval2 is not eval_
    assert eval2.id == eval_.id
    assert eval2.criteria[0] is not eval_.criteria[0]
    assert eval2.criteria[0].id == eval_.criteria[0].id

def test_evaluation_unique_ids():
    crit1 = make_criterion("crit1", 2)
    crit2 = make_criterion("crit1", 3)  # duplicate id
    with pytest.raises(ValueError) as excinfo:
        Evaluation(id="eval5", name="Eval Dups", criteria=[crit1, crit2])
    assert "doivent être uniques" in str(excinfo.value)

def test_evaluation_invalid_excel_id():
    crit = make_criterion("crit1", 2)
    # id with space is not safe for Excel named cell
    with pytest.raises(ValueError) as excinfo:
        Evaluation(id="invalid id", name="Eval Excel", criteria=[crit])
    assert "n'est pas valide pour une cellule Excel" in str(excinfo.value)
