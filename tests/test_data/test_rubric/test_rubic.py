from decimal import Decimal

import pytest
from pydantic import ValidationError

from c3hm.data.evaluation.criterion import Criterion
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.evaluation.indicator import Indicator
from c3hm.data.rubric.descriptors import Descriptors
from c3hm.data.rubric.format import Format
from c3hm.data.rubric.grade_level import GradeLevel
from c3hm.data.rubric.grade_levels import GradeLevels
from c3hm.data.rubric.rubric import Rubric


def make_indicator(id="ind1", grade=Decimal("2"), points=Decimal("2")):
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

def make_grade_level(name="Excellent", max_percentage=Decimal("20"), min_percentage=Decimal("16")):
    return GradeLevel(
        name=name,
        max_percentage=max_percentage,
        min_percentage=min_percentage
    )

def make_evaluation(name="Test Evaluation", criteria=None):
    if criteria is None:
        criteria = [make_criterion()]
    return Evaluation(
        name=name,
        grade_step=Decimal("1"),
        criteria=criteria,
        override_grade=None,
        comment=""
    )

def make_rubric(grade_levels: GradeLevels, evaluation: Evaluation,
                descriptors: Descriptors | None = None):
    if descriptors is None:
        d = {}
        for c in evaluation.criteria:
            for i in c.indicators:
                for lvl in grade_levels.levels:
                    key = (i.id, lvl.name)
                    d[key] = "Descriptor"
        descriptors = Descriptors(descriptors=d)

    return Rubric(
        grade_levels=grade_levels,
        evaluation=evaluation,
        format = Format(),
        descriptors=descriptors,
    )

def test_rubric_valid_creation():
    criteria = [make_criterion(id="crit1"), make_criterion(id="crit2")]
    grade_levels = [
        make_grade_level(name="Excellent", max_percentage=Decimal("20"),
                         min_percentage=Decimal("16")),
        make_grade_level(name="Bon", max_percentage=Decimal("15"), min_percentage=Decimal("10")),
    ]
    evaluation = make_evaluation(criteria=criteria)
    rubric = make_rubric(
        grade_levels=GradeLevels(levels=grade_levels),
        evaluation=evaluation,
    )
    assert rubric.grade_levels == GradeLevels(levels=grade_levels)
    assert rubric.evaluation == evaluation
    assert rubric.descriptors.contains(criteria[0].indicators[0], grade_levels[0])

    d = rubric.to_dict()
    rubric2 = Rubric.from_dict(d)
    assert rubric2 == rubric

    rubric_copy = rubric.copy()
    assert rubric_copy is not rubric
    assert rubric_copy == rubric

def test_rubric_invalid_descriptor():
    criteria = [make_criterion(id="crit1"), make_criterion(id="crit2")]
    grade_levels = [
        make_grade_level(name="Excellent", max_percentage=Decimal("20"),
                         min_percentage=Decimal("16")),
        make_grade_level(name="Bon", max_percentage=Decimal("15"), min_percentage=Decimal("10")),
    ]
    evaluation = make_evaluation(criteria=criteria)
    with pytest.raises(ValidationError):
        Rubric(
            grade_levels=GradeLevels(levels=grade_levels),
            evaluation=evaluation,
            format=Format(),
            descriptors=Descriptors(descriptors={}),
        )

    rubric = make_rubric(
        grade_levels=GradeLevels(levels=grade_levels),
        evaluation=evaluation,
    )
    rdict = rubric.to_dict()
    d = rdict["descripteurs"]
    del d[("ind1", "Excellent")]
    with pytest.raises(ValidationError):
        Rubric.from_dict(rdict)
