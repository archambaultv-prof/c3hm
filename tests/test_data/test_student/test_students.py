import pytest

from c3hm.data.student.student import Student
from c3hm.data.student.students import Students


def make_student(
    first_name="John",
    last_name="Doe",
    alias="alias1",
    omnivox_code="1234567",
    team="",
    is_team_reference=False,
):
    # Minimal Student mock for testing
    return Student(
        first_name=first_name,
        last_name=last_name,
        alias=alias,
        omnivox_code=omnivox_code,
        team=team,
        is_team_reference=is_team_reference,
    )

def test_students_unique_aliases():
    students = [
        make_student(first_name="Alice", last_name="Smith", alias="a1"),
        make_student(first_name="Bob", last_name="Jones", alias="a2")
    ]
    s = Students(students=students)
    assert len(s.students) == 2

def test_students_duplicate_aliases_raises():
    students = [
        make_student(first_name="Alice", last_name="Smith", alias="dup"),
        make_student(first_name="Bob", last_name="Jones", alias="dup")
    ]
    with pytest.raises(ValueError):
        Students(students=students)

def test_students_team_reference_unique_per_team():
    students = [
        make_student(first_name="Alice", last_name="Smith", alias="a1", team="t1",
                     is_team_reference=True),
        make_student(first_name="Bob", last_name="Jones", alias="a2", team="t1",
                     is_team_reference=False),
        make_student(first_name="Carol", last_name="Brown", alias="a3", team="t2",
                     is_team_reference=True),
    ]
    s = Students(students=students)
    assert len(s.students) == 3

def test_students_team_reference_missing_raises():
    students = [
        make_student(first_name="Alice", last_name="Smith", alias="a1", team="t1",
                     is_team_reference=False),
        make_student(first_name="Bob", last_name="Jones", alias="a2", team="t1",
                     is_team_reference=False),
    ]
    with pytest.raises(ValueError):
        Students(students=students)

def test_students_team_reference_duplicate_raises():
    students = [
        make_student(first_name="Alice", last_name="Smith", alias="a1", team="t1",
                     is_team_reference=True),
        make_student(first_name="Bob", last_name="Jones", alias="a2", team="t1",
                     is_team_reference=True),
    ]
    with pytest.raises(ValueError):
        Students(students=students)

def test_students_find_student_found():
    students = [
        make_student(first_name="Alice", last_name="Smith", omnivox_code="111", alias="a1"),
        make_student(first_name="Bob", last_name="Jones", omnivox_code="222", alias="a2"),
    ]
    s = Students(students=students)
    found = s.find_student("222")
    assert found is not None
    assert found.first_name == "Bob"

def test_students_find_student_not_found():
    students = [
        make_student(first_name="Alice", last_name="Smith", omnivox_code="111")
    ]
    s = Students(students=students)
    found = s.find_student("999")
    assert found is None

def test_students_find_other_team_members():
    s1 = make_student(first_name="Alice", last_name="Smith", alias="a1", omnivox_code="1",
                      team="t1", is_team_reference=True)
    s2 = make_student(first_name="Bob", last_name="Jones", alias="a2", omnivox_code="2",
                      team="t1")
    s3 = make_student(first_name="Carol", last_name="Brown", alias="a3", omnivox_code="3",
                      team="t2", is_team_reference=True)
    s = Students(students=[s1, s2, s3])
    others = s.find_other_team_members(s1)
    assert len(others) == 1
    assert others[0].omnivox_code == "2"

def test_students_iter():
    students = [
        make_student(first_name="Alice", last_name="Smith", alias="a1"),
        make_student(first_name="Bob", last_name="Jones", alias="a2")
    ]
    s = Students(students=students)
    aliases = [student.alias for student in s]
    assert aliases == ["a1", "a2"]
