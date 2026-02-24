"""Tests for c3hm.data.student module."""

import csv

import pytest

from c3hm.data.student import Student, find_student_by_name, read_omnivox_students_file


class TestStudent:
    """Tests for Student class."""

    def test_student_initialization(self):
        """Test Student object initialization."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        assert student.omnivox_id == "12345"
        assert student.firstname == "Jean"
        assert student.surname == "Dupont"

    def test_fullname_default(self):
        """Test fullname with default parameters."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        assert student.fullname() == "Jean Dupont"

    def test_fullname_surname_first(self):
        """Test fullname with surname first."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        assert student.fullname(surname_first=True) == "Dupont Jean"

    def test_fullname_with_omnivox(self):
        """Test fullname with omnivox ID included."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        assert student.fullname(include_omnivox=True) == "Jean Dupont 12345"

    def test_fullname_custom_separator(self):
        """Test fullname with custom separator."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        assert student.fullname(separator=", ") == "Jean, Dupont"

    def test_fullname_all_options(self):
        """Test fullname with all options."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        result = student.fullname(surname_first=True, include_omnivox=True, separator=", ")
        assert result == "Dupont, Jean, 12345"

    def test_validate_valid_student(self):
        """Test validation of valid student."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        # Should not raise
        student.validate()

    def test_validate_empty_omnivox_id_raises_error(self):
        """Test that empty omnivox_id raises ValueError."""
        student = Student(omnivox_id="", firstname="Jean", surname="Dupont")
        with pytest.raises(ValueError, match=r"L'identifiant Omnivox ne peut pas être vide"):
            student.validate()

    def test_validate_whitespace_omnivox_id_raises_error(self):
        """Test that whitespace-only omnivox_id raises ValueError."""
        student = Student(omnivox_id="   ", firstname="Jean", surname="Dupont")
        with pytest.raises(ValueError, match=r"L'identifiant Omnivox ne peut pas être vide"):
            student.validate()

    def test_validate_empty_firstname_raises_error(self):
        """Test that empty firstname raises ValueError."""
        student = Student(omnivox_id="12345", firstname="", surname="Dupont")
        with pytest.raises(ValueError, match=r"Le prénom de l'étudiant ne peut pas être vide"):
            student.validate()

    def test_validate_whitespace_firstname_raises_error(self):
        """Test that whitespace-only firstname raises ValueError."""
        student = Student(omnivox_id="12345", firstname="   ", surname="Dupont")
        with pytest.raises(ValueError, match=r"Le prénom de l'étudiant ne peut pas être vide"):
            student.validate()

    def test_validate_empty_surname_raises_error(self):
        """Test that empty surname raises ValueError."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="")
        with pytest.raises(ValueError, match=r"Le nom de famille de l'étudiant ne peut pas être vide"):
            student.validate()

    def test_validate_whitespace_surname_raises_error(self):
        """Test that whitespace-only surname raises ValueError."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="   ")
        with pytest.raises(ValueError, match=r"Le nom de famille de l'étudiant ne peut pas être vide"):
            student.validate()

    def test_to_dict(self):
        """Test serialization to dict."""
        student = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        data = student.to_dict()
        assert data == {"matricule": "12345", "prénom": "Jean", "nom": "Dupont"}

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {"matricule": "12345", "prénom": "Jean", "nom": "Dupont"}
        student = Student.from_dict(data)
        assert student.omnivox_id == "12345"
        assert student.firstname == "Jean"
        assert student.surname == "Dupont"

    def test_from_dict_missing_keys_defaults_to_empty(self):
        """Test deserialization with missing keys defaults to empty strings."""
        data = {"matricule": "12345"}
        student = Student.from_dict(data)
        assert student.omnivox_id == "12345"
        assert student.firstname == ""
        assert student.surname == ""

    def test_copy(self):
        """Test that copy creates a copy."""
        original = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        copied = original.copy()
        assert copied.omnivox_id == original.omnivox_id
        assert copied.firstname == original.firstname
        assert copied.surname == original.surname

    def test_round_trip_serialization(self):
        """Test round-trip serialization."""
        original = Student(omnivox_id="12345", firstname="Jean", surname="Dupont")
        data = original.to_dict()
        restored = Student.from_dict(data)
        assert restored.omnivox_id == original.omnivox_id
        assert restored.firstname == original.firstname
        assert restored.surname == original.surname


class TestFindStudentByName:
    """Tests for find_student_by_name function."""

    def test_find_student_exact_match(self):
        """Test finding student with exact name match."""
        students = [
            Student(omnivox_id="1", firstname="Jean", surname="Dupont"),
            Student(omnivox_id="2", firstname="Marie", surname="Martin"),
        ]
        student = find_student_by_name("Jean Dupont", students)
        assert student.omnivox_id == "1"

    def test_find_student_case_insensitive(self):
        """Test finding student with case-insensitive match."""
        students = [Student(omnivox_id="1", firstname="Jean", surname="Dupont")]
        student = find_student_by_name("JEAN DUPONT", students)
        assert student.omnivox_id == "1"

    def test_find_student_partial_name(self):
        """Test finding student with partial name."""
        students = [Student(omnivox_id="1", firstname="Jean", surname="Dupont")]
        student = find_student_by_name("Jean", students)
        assert student.omnivox_id == "1"

    def test_find_student_surname_only(self):
        """Test finding student with surname only."""
        students = [Student(omnivox_id="1", firstname="Jean", surname="Dupont")]
        student = find_student_by_name("Dupont", students)
        assert student.omnivox_id == "1"

    def test_find_student_multiple_tokens(self):
        """Test finding student with multiple tokens."""
        students = [
            Student(omnivox_id="1", firstname="Jean", surname="Dupont"),
            Student(omnivox_id="2", firstname="Marie", surname="Dupont"),
        ]
        student = find_student_by_name("Jean Dupont", students)
        assert student.omnivox_id == "1"

    def test_find_student_not_found_raises_error(self):
        """Test that non-existent student raises ValueError."""
        students = [Student(omnivox_id="1", firstname="Jean", surname="Dupont")]
        with pytest.raises(ValueError, match=r"No student found"):
            find_student_by_name("Unknown", students)

    def test_find_student_multiple_matches_raises_error(self):
        """Test that multiple matches raise ValueError."""
        students = [
            Student(omnivox_id="1", firstname="Jean", surname="Dupont"),
            Student(omnivox_id="2", firstname="Jean", surname="Dupont"),
        ]
        with pytest.raises(ValueError, match=r"Multiple students found"):
            find_student_by_name("Jean", students)


class TestReadOmnivoxStudentsFile:
    """Tests for read_omnivox_students_file function."""

    def test_read_omnivox_students_file_valid(self, tmp_path):
        """Test reading valid Omnivox CSV file."""
        # Create a temporary CSV file
        # Omnivox format: XX<value> with one trailing character (space or padding)
        csv_file = tmp_path / "students.csv"
        with open(csv_file, "w", encoding="iso-8859-1", newline="") as f:
            writer = csv.writer(f, quotechar='"')
            writer.writerow(["No de dossier", "Prénom de l'étudiant", "Nom de l'étudiant"])
            writer.writerow(["XX12345 ", "XXJEAN ", "XXDUPONT "])
            writer.writerow(["XX12346 ", "XXMARIE ", "XXMARTIN "])

        students = read_omnivox_students_file(csv_file)
        assert len(students) == 2
        assert students[0].omnivox_id == "12345"
        assert students[0].firstname == "JEAN"
        assert students[0].surname == "DUPONT"
        assert students[1].omnivox_id == "12346"

    def test_read_omnivox_students_file_strips_padding(self, tmp_path):
        """Test that Omnivox padding is stripped correctly."""
        csv_file = tmp_path / "students.csv"
        with open(csv_file, "w", encoding="iso-8859-1", newline="") as f:
            writer = csv.writer(f, quotechar='"')
            writer.writerow(["No de dossier", "Prénom de l'étudiant", "Nom de l'étudiant"])
            writer.writerow(["XXABC123 ", "XXALAIN ", "XXJOURDAN "])

        students = read_omnivox_students_file(csv_file)
        assert students[0].omnivox_id == "ABC123"
        assert students[0].firstname == "ALAIN"
        assert students[0].surname == "JOURDAN"

    def test_read_omnivox_students_file_with_accents(self, tmp_path):
        """Test reading CSV with accented characters."""
        csv_file = tmp_path / "students.csv"
        with open(csv_file, "w", encoding="iso-8859-1", newline="") as f:
            writer = csv.writer(f, quotechar='"')
            writer.writerow(["No de dossier", "Prénom de l'étudiant", "Nom de l'étudiant"])
            writer.writerow(["XX12345 ", "XXJÉRÔME ", "XXBÉRUBÉ "])

        students = read_omnivox_students_file(csv_file)
        assert students[0].firstname == "JÉRÔME"
        assert students[0].surname == "BÉRUBÉ"

    def test_read_omnivox_students_file_empty_file(self, tmp_path):
        """Test reading CSV with header only."""
        csv_file = tmp_path / "students.csv"
        with open(csv_file, "w", encoding="iso-8859-1", newline="") as f:
            writer = csv.writer(f, quotechar='"')
            writer.writerow(["No de dossier", "Prénom de l'étudiant", "Nom de l'étudiant"])

        students = read_omnivox_students_file(csv_file)
        assert len(students) == 0

    def test_read_omnivox_students_file_nonexistent_raises_error(self, tmp_path):
        """Test that nonexistent file raises error."""
        csv_file = tmp_path / "nonexistent.csv"
        with pytest.raises(FileNotFoundError):
            read_omnivox_students_file(csv_file)
