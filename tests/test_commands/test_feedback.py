from pathlib import Path

import openpyxl

from c3hm.commands.feedback import grades_from_wb
from c3hm.data.config.config_parser import config_from_yaml
from c3hm.data.student.students import Students


def test_graded_rubrics_from_wb(
    config_full_template_path: Path,
    student_list_csv_path: Path,
    gradebook_path: Path,
):
    """
    Teste la fonction grades_from_wb.
    """

    # Charge la configuration et la grille d'évaluation
    config = config_from_yaml(config_full_template_path)
    config.students = student_list_csv_path
    students = Students.from_file(config.students)

    # Ouvre le gradebook
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config, students=students)

    # Vérifie que le nombre est correct
    assert len(grades) == 3

def test_graded_rubrics_from_wb_inference(
    config_full_template_path: Path,
    student_list_csv_path: Path,
    gradebook2_path: Path,
):
    """
    Teste la fonction grades_from_wb.
    """

    # Charge la configuration et la grille d'évaluation
    config = config_from_yaml(config_full_template_path)
    config.students = student_list_csv_path
    students = Students.from_file(config.students)

    # Ouvre le gradebook
    wb = openpyxl.load_workbook(gradebook2_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config, students=students)

    # Vérifie que le nombre est correct
    assert len(grades) == 3
