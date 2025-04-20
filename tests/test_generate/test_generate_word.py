from pathlib import Path

from c3hm.core.generate.generate_word import generate_word_from_rubric
from c3hm.core.rubric import load_rubric_from_yaml


def test_generate_word_from_rubric_1(
        rubric_1_path: Path,
        tmp_path: Path,
        output_dir: Path):
    _test_generate_word_from_rubric(
        rubric_1_path,
        tmp_path,
        output_dir)

def test_generate_word_from_rubric_template_5(
        rubric_template_5_path: Path,
        tmp_path: Path,
        output_dir: Path):
    _test_generate_word_from_rubric(
        rubric_template_5_path,
        tmp_path,
        output_dir)

def _test_generate_word_from_rubric(
        rubric_path_: Path,
        tmp_path_: Path,
        output_dir_: Path):
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    r = load_rubric_from_yaml(rubric_path_)
    doc_file = tmp_path_ / rubric_path_.with_suffix(".docx")
    generate_word_from_rubric(r, doc_file)
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir_ / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)
