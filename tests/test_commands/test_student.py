import sys
from pathlib import Path

from c3hm.commands.student import generate_rubric, word_to_pdf
from c3hm.data.config import Config


def test_generate_word_from_rubric(
        config_template_5_path: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    config = Config.from_yaml(config_template_5_path)
    doc_file = tmp_path / config_template_5_path.with_suffix(".docx")
    generate_rubric(config.rubric, doc_file, title=config.title())
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)

    # Sur windows, on test aussi la convertion en PDF
    if sys.platform == "win32":
        word_to_pdf(output_path, output_path.with_suffix(".pdf"))
        assert output_path.with_suffix(".pdf").exists()
