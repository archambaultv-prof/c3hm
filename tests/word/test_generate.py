from pathlib import Path

from c3hm.core.rubric import load_rubric_from_yaml
from c3hm.core.word.generate import generate_word_from_rubric


def test_generate_word_from_rubric(
        rubric_1_path: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    r = load_rubric_from_yaml(rubric_1_path)
    doc_file = tmp_path / rubric_1_path.with_suffix(".docx")
    generate_word_from_rubric(r, doc_file)
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)
