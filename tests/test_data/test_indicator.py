from decimal import Decimal

import pytest

from c3hm.data.tmp.excelid import ExcelID
from c3hm.data.rubric.grade import Grade
from c3hm.data.tmp.indicator import Indicator


@pytest.fixture
def excel_id():
    return ExcelID(xl_cell_id_base="I1")

@pytest.fixture
def grade():
    return Grade(value=Decimal("85.5"), comment="Good job")

def test_indicator_creation(excel_id):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=None
    )
    assert indicator.name == "Clarity"
    assert indicator.points == Decimal("25")
    assert indicator.descriptors == ["Clear", "Concise"]
    assert indicator.excel_id == excel_id
    assert indicator.grade is None

def test_indicator_has_grade_true(excel_id, grade):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=grade
    )
    assert indicator.has_grade is True

def test_indicator_has_grade_false(excel_id):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=None
    )
    assert indicator.has_grade is False

def test_indicator_has_comment_true(excel_id, grade):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=grade
    )
    assert indicator.has_comment is True

def test_indicator_has_comment_false(excel_id):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=None
    )
    assert indicator.has_comment is False

def test_get_grade_value_success(excel_id, grade):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=grade
    )
    assert indicator.get_grade_value() == Decimal("85.5")

def test_get_grade_value_raises(excel_id):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=None
    )
    with pytest.raises(ValueError):
        indicator.get_grade_value()

def test_to_dict_with_and_without_decimal(excel_id, grade):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25.5"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=grade
    )
    d1 = indicator.to_dict()
    d2 = indicator.to_dict(convert_decimal=True)
    assert d1["nom"] == "Clarity"
    assert d1["pourcentage"] == Decimal("25.5")
    assert isinstance(d2["pourcentage"], float)

def test_from_dict_and_copy(excel_id, grade):
    indicator = Indicator(
        name="Clarity",
        points=Decimal("25"),
        descriptors=["Clear", "Concise"],
        excel_id=excel_id,
        grade=grade
    )
    d = indicator.to_dict()
    assert indicator.grade is not None
    indicator2 = Indicator.from_dict(d)
    assert indicator2.name == indicator.name
    assert indicator2.points == indicator.points
    assert indicator2.descriptors == indicator.descriptors
    assert indicator2.excel_id == indicator.excel_id
    assert indicator2.grade is not None
    assert indicator2.grade.value == indicator.grade.value

    indicator3 = indicator.copy()
    assert indicator3 is not indicator
    assert indicator3.name == indicator.name
    assert indicator3.descriptors == indicator.descriptors
    assert indicator3.excel_id == indicator.excel_id
    assert indicator3.grade is not None
    assert indicator3.grade.value == indicator.grade.value

def test_indicator_min_length_constraints(excel_id):
    with pytest.raises(ValueError):
        Indicator(
            name="",
            points=Decimal("10"),
            descriptors=["desc"],
            excel_id=excel_id
        )
    with pytest.raises(ValueError):
        Indicator(
            name="Valid",
            points=Decimal("10"),
            descriptors=[],
            excel_id=excel_id
        )

def test_indicator_percentage_constraints(excel_id):
    with pytest.raises(ValueError):
        Indicator(
            name="Valid",
            points=Decimal("-1"),
            descriptors=["desc"],
            excel_id=excel_id
        )
    with pytest.raises(ValueError):
        Indicator(
            name="Valid",
            points=Decimal("101"),
            descriptors=["desc"],
            excel_id=excel_id
        )
