from decimal import Decimal

import pytest

from c3hm.data.tmp.criterion import Criterion
from c3hm.data.tmp.excelid import ExcelID
from c3hm.data.rubric.grade import Grade
from c3hm.data.tmp.indicator import Indicator


@pytest.fixture
def indicator():
    return Indicator(
        name="Test Indicator",
        points=Decimal("50"),
        descriptors=["Descriptor 1", "Descriptor 2"],
        excel_id= ExcelID(xl_cell_id_base="C1_I1"),
        grade=Grade(value=Decimal("85"), comment="Good work")
    )

@pytest.fixture
def excel_id():
    return ExcelID(xl_cell_id_base="C1")

@pytest.fixture
def grade():
    return Grade(value=Decimal("95"), comment="Excellent")

def test_criterion_has_specific_comment_with_grade(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    assert criterion.has_specific_comment is True

def test_criterion_has_specific_comment_without_grade(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.has_specific_comment is False

def test_criterion_has_specific_grade(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    assert criterion.has_specific_grade is True

def test_criterion_has_specific_grade_none(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.has_specific_grade is False

def test_get_specific_grade_returns_grade(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    assert criterion.get_specific_grade() == grade

def test_get_specific_grade_raises_without_grade(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    with pytest.raises(ValueError):
        criterion.get_specific_grade()

def test_has_grade_with_grade(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    assert criterion.has_grade is True

def test_has_grade_with_all_indicators(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.has_grade is True

def test_has_grade_with_no_grade_and_indicator_no_grade(indicator, excel_id):
    indicator2 = indicator.copy()
    indicator2.grade = None  # Ensure this indicator has no grade
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator2],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.has_grade is False

def test_has_comments_with_specific_comment(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    assert criterion.has_comments is True

def test_has_comments_with_indicator_comment(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.has_comments is True

def test_percentage_sum(indicator, excel_id):
    indicator1 = indicator.copy()
    indicator1.percentage = Decimal("30")
    indicator2 = indicator.copy()
    indicator2.percentage = Decimal("70")
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator1, indicator2],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.points == Decimal("100")

def test_get_grade_value_with_grade(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    assert criterion.get_weighted_grade_value() == grade.value

def test_get_grade_value_with_indicators(indicator, excel_id):
    indicator1 = indicator.copy()
    indicator1.grade.value = Decimal("2.0")
    indicator2 = Indicator(
        name="Indicator 2",
        points=Decimal("0.5"),
        grade=Grade(value=Decimal("3.0"))
    )
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator1, indicator2],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.get_weighted_grade_value() == Decimal("5.0")

def test_get_grade_value_raises_when_no_grades(excel_id):
    indicator = Indicator(name="No Grade Indicator", points=Decimal("1.0"))
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    with pytest.raises(ValueError):
        criterion.get_weighted_grade_value()

def test_nb_indicators(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator, indicator],
        excel_id=excel_id,
        grade=None
    )
    assert criterion.nb_indicators() == 2

def test_to_dict_with_grade(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    d = criterion.to_dict()
    assert d["critère"] == "Critère 1"
    assert d["indicateurs"] == [indicator.to_dict()]
    assert d["xl id"] == excel_id.to_dict()
    assert d["grade"] == grade.to_dict()

def test_to_dict_without_grade(indicator, excel_id):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=None
    )
    d = criterion.to_dict()
    assert d["grade"] is None

def test_from_dict(indicator, excel_id, grade):
    data = {
        "critère": "Critère 1",
        "indicateurs": [indicator.to_dict()],
        "xl id": excel_id.to_dict(),
        "grade": grade.to_dict()
    }
    crit = Criterion.from_dict(data)
    assert crit.name == "Critère 1"
    assert len(crit.indicators) == 1
    assert crit.excel_id.sheet == excel_id.sheet
    assert crit.excel_id.cell == excel_id.cell
    assert crit.grade.value == grade.value

def test_copy(indicator, excel_id, grade):
    criterion = Criterion(
        name="Critère 1",
        indicators=[indicator],
        excel_id=excel_id,
        grade=grade
    )
    copy_criterion = criterion.copy()
    assert copy_criterion is not criterion
    assert copy_criterion.name == criterion.name
    assert copy_criterion.indicators == criterion.indicators
    assert copy_criterion.excel_id == criterion.excel_id
    assert copy_criterion.grade == criterion.grade