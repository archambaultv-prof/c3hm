import pytest

from c3hm.data.student.student import Student


def test_student_creation_and_fields():
    student = Student(
        first_name="Alice",
        last_name="Smith",
        omnivox_code="12345",
        alias="asmith",
        team="TeamA",
        is_team_reference=True
    )
    assert student.first_name == "Alice"
    assert student.last_name == "Smith"
    assert student.omnivox_code == "12345"
    assert student.alias == "asmith"
    assert student.team == "TeamA"
    assert student.is_team_reference is True

def test_student_strip_fields():
    student = Student(
        first_name="  Bob ",
        last_name="  Brown ",
        omnivox_code="  67890 ",
        alias=" bbrown ",
        team="  TeamB  "
    )
    assert student.first_name == "Bob"
    assert student.last_name == "Brown"
    assert student.omnivox_code == "67890"
    assert student.alias == "bbrown"
    assert student.team == "TeamB"

def test_student_empty_fields_raises():
    with pytest.raises(ValueError):
        Student(
            first_name=" ",
            last_name="Doe",
            omnivox_code="11111",
            alias="jdoe"
        )
    with pytest.raises(ValueError):
        Student(
            first_name="John",
            last_name=" ",
            omnivox_code="11111",
            alias="jdoe"
        )
    with pytest.raises(ValueError):
        Student(
            first_name="John",
            last_name="Doe",
            omnivox_code=" ",
            alias="jdoe"
        )
    with pytest.raises(ValueError):
        Student(
            first_name="John",
            last_name="Doe",
            omnivox_code="11111",
            alias=" "
        )

def test_student_team_none_when_empty():
    student = Student(
        first_name="Jane",
        last_name="Doe",
        omnivox_code="22222",
        alias="jdoe",
        team="   "
    )
    assert student.team is None

def test_student_has_team():
    student = Student(
        first_name="Tom",
        last_name="Jones",
        omnivox_code="33333",
        alias="tjones",
        team="TeamC"
    )
    assert student.has_team() is True
    student_no_team = Student(
        first_name="Tom",
        last_name="Jones",
        omnivox_code="33333",
        alias="tjones"
    )
    assert student_no_team.has_team() is False

def test_student_ws_name():
    student = Student(
        first_name="Anna",
        last_name="Lee",
        omnivox_code="44444",
        alias="alee"
    )
    assert student.ws_name() == "alee"
