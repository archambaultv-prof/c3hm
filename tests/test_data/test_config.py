from pathlib import Path

import pytest

from c3hm.data.config import Config, read_student_csv
from c3hm.data.student import Student


def test_config(
        config_template_path: Path,
        student_list_path: Path
    ) -> None:
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    # Test avec le gabarit
    config = Config.from_yaml(config_template_path)

    # Test read_student_csv
    students_dict = read_student_csv(student_list_path)
    students = [
        Student.from_dict(student) for student in students_dict
    ]
    assert config.students == students

    # Test from_dict
    d = config.to_dict()
    d["étudiants"] = student_list_path
    config2 = Config.from_dict(d)

    assert config2.students == config.students

def test_wrong_grade_weights(
        config_template_path: Path
    ) -> None:
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    # Test avec le gabarit
    config = Config.from_yaml(config_template_path)

    config.rubric.criteria[0].indicators[0].grade_weights = [0.5, 0.5]  # Not the same length

    with pytest.raises(ValueError):
        config.validate_config()
