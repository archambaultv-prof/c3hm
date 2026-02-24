"""Tests for c3hm.data.rubric module."""

import pytest

from c3hm.data.criterion import Criterion
from c3hm.data.grid import Grid
from c3hm.data.indicator import Indicator
from c3hm.data.level import DEFAULT_LEVELS
from c3hm.data.rubric import Rubric, validate_rubrics, validate_teammates
from c3hm.data.student import Student


class TestRubric:
    """Tests for Rubric class."""

    def test_rubric_initialization_minimal(self):
        """Test Rubric initialization with minimal parameters."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid)
        assert rubric.course == "CS101"
        assert rubric.session == "Hiver 2025"
        assert rubric.evaluation == "Eval 1"
        assert rubric.student is None
        assert rubric.teammates == []
        assert rubric.grade_override is None
        assert rubric.comment is None

    def test_rubric_initialization_with_student(self):
        """Test Rubric initialization with student."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid, student=student)
        assert rubric.student is not None
        assert rubric.student == student
        assert rubric.student.omnivox_id == "12345"

    def test_rubric_initialization_with_teammates(self):
        """Test Rubric initialization with teammates."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        teammate = Student(omnivox_id="12346", firstname="Marie", surname="Martin")
        rubric = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            student=student,
            teammates=[teammate],
        )
        assert len(rubric.teammates) == 1
        assert rubric.teammates[0].omnivox_id == "12346"

    def test_validate_valid_rubric(self):
        """Test validation of valid rubric."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid)
        # Should not raise
        rubric.validate()

    def test_validate_empty_course_raises_error(self):
        """Test that empty course raises ValueError."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="", session="Hiver 2025", evaluation="Eval 1", grid=grid)
        with pytest.raises(ValueError, match=r"Le champ 'cours' doit être une chaîne"):
            rubric.validate()

    def test_validate_empty_session_raises_error(self):
        """Test that empty session raises ValueError."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="CS101", session="", evaluation="Eval 1", grid=grid)
        with pytest.raises(ValueError, match=r"Le champ 'session'"):
            rubric.validate()

    def test_validate_empty_evaluation_raises_error(self):
        """Test that empty evaluation raises ValueError."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="", grid=grid)
        with pytest.raises(ValueError, match=r"Le champ 'évaluation'"):
            rubric.validate()

    def test_validate_grade_override_negative_raises_error(self):
        """Test that negative grade override raises ValueError."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            grade_override=-1,
        )
        with pytest.raises(ValueError, match=r"La note doit être un nombre entre 0 et 100"):
            rubric.validate()

    def test_validate_grade_override_exceeds_100_raises_error(self):
        """Test that grade override > 100 raises ValueError."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            grade_override=101,
        )
        with pytest.raises(ValueError, match=r"La note doit être un nombre entre 0 et 100"):
            rubric.validate()

    def test_final_grade_returns_override(self):
        """Test that final_grade returns override if set."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[
                        Indicator(
                            label="Ind",
                            points=100,
                            descriptors=["D"] * 5,
                            graded_level="Bien maîtrisé",
                        )
                    ],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            grade_override=75,
        )
        assert rubric.final_grade() == 75

    def test_final_grade_returns_grid_grade_if_no_override(self):
        """Test that final_grade returns grid grade if no override."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[
                        Indicator(
                            label="Ind",
                            points=100,
                            descriptors=["D"] * 5,
                            graded_level="Acquis",
                        )
                    ],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid)
        # 100 * 0.75 = 75
        assert rubric.final_grade() == 75

    def test_grid_grade(self):
        """Test grid_grade method."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[
                        Indicator(
                            label="Ind",
                            points=100,
                            descriptors=["D"] * 5,
                            graded_level="Bien maîtrisé",
                        )
                    ],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            grade_override=50,
        )
        assert rubric.grid_grade() == 100  # Ignores override

    def test_copy(self):
        """Test that copy creates a deep copy."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        original = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            student=student,
            grade_override=75,
            comment="Good work",
        )
        copied = original.copy()

        assert copied.course == original.course
        assert copied.student is not None
        assert original.student is not None
        assert copied.student.omnivox_id == original.student.omnivox_id
        assert copied.grade_override == original.grade_override

        # Modify copy
        copied.course = "CS102"
        copied.grade_override = 50

        # Original should be unchanged
        assert original.course == "CS101"
        assert original.grade_override == 75

    def test_to_dict_without_student(self):
        """Test serialization without student."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid)
        data = rubric.to_dict()
        assert data["cours"] == "CS101"
        assert data["session"] == "Hiver 2025"
        assert data["évaluation"] == "Eval 1"
        assert "étudiant" not in data

    def test_to_dict_with_student(self):
        """Test serialization with student."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid, student=student)
        data = rubric.to_dict()
        assert "étudiant" in data
        assert data["étudiant"]["matricule"] == "12345"

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "cours": "CS101",
            "session": "Hiver 2025",
            "évaluation": "Eval 1",
            "grille": {
                "afficher les points des critères": True,
                "afficher les pourcentages des niveaux": True,
                "niveaux": [
                    {"niveau": "Excellent", "pourcentage": 1.0, "abréviations": ["e"]},
                ],
                "critères": [
                    {
                        "critère": "Criterion",
                        "indicateurs": [
                            {"indicateur": "Ind", "points": 100, "descripteurs": ["D"]},
                        ],
                    }
                ],
            },
        }
        rubric = Rubric.from_dict(data)
        assert rubric.course == "CS101"
        assert rubric.session == "Hiver 2025"
        assert rubric.evaluation == "Eval 1"

    def test_template(self):
        """Test template generation."""
        rubric = Rubric.template()
        assert isinstance(rubric, Rubric)
        assert len(rubric.grid.criteria) == 2
        assert rubric.grid.criteria[0].points() != 0
        assert rubric.grid.criteria[1].points() != 0


class TestValidateRubrics:
    """Tests for validate_rubrics function."""

    def test_validate_rubrics_valid(self):
        """Test validation of valid rubrics."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        rubric = Rubric(course="CS101", session="Hiver 2025", evaluation="Eval 1", grid=grid, student=student)
        # Should not raise
        validate_rubrics([rubric])

    def test_validate_rubrics_invalid_raises_error(self):
        """Test that invalid rubric raises error."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        rubric = Rubric(course="", session="Hiver 2025", evaluation="Eval 1", grid=grid)
        with pytest.raises(ValueError):
            validate_rubrics([rubric])


class TestValidateTeammates:
    """Tests for validate_teammates function."""

    def test_validate_teammates_valid(self):
        """Test validation of valid teammate relationships."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student1 = Student(omnivox_id="1", firstname="Student", surname="One")
        student2 = Student(omnivox_id="2", firstname="Student", surname="Two")
        rubric1 = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            student=student1,
            teammates=[student2],
        )
        rubric2 = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            student=student2,
            teammates=[student1],
        )
        # Should not raise
        validate_teammates([rubric1, rubric2])

    def test_validate_teammates_asymmetric_raises_error(self):
        """Test that asymmetric teammate relationships raise error."""
        grid = Grid(
            criteria=[
                Criterion(
                    label="Criterion",
                    indicators=[Indicator(label="Ind", points=100, descriptors=["D"] * 5)],
                )
            ],
            levels=DEFAULT_LEVELS,
        )
        student1 = Student(omnivox_id="1", firstname="Student", surname="One")
        student2 = Student(omnivox_id="2", firstname="Student", surname="Two")
        rubric1 = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            student=student1,
            teammates=[student2],  # Has teammate
        )
        rubric2 = Rubric(
            course="CS101",
            session="Hiver 2025",
            evaluation="Eval 1",
            grid=grid,
            student=student2,
            teammates=[],  # Doesn't have student1 as teammate
        )
        with pytest.raises(ValueError, match=r"Incohérence dans les coéquipiers"):
            validate_teammates([rubric1, rubric2])
