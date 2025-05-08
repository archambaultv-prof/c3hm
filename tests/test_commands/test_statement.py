import sys
from pathlib import Path

from c3hm.commands.generate_rubric import word_to_pdf
from c3hm.commands.statement import generate_statement_rubric
from c3hm.data.config import Config


def test_generate_word_from_rubric(
        config_template_path: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    # Test avec le gabarit
    config = Config.from_yaml(config_template_path)
    doc_file = tmp_path / config_template_path.with_suffix(".docx")
    generate_rubric(doc_file, output_dir, config)

    # Test avec le gabarit sans pondération des indicateurs
    c_1 = config.copy()
    c_1.rubric.format.hide_indicators_weight = True
    doc_file = tmp_path / f"{config_template_path.stem}_no_weights.docx"
    generate_rubric(doc_file, output_dir, c_1)

    # Retire les descripteurs
    c_no_descriptors = config.copy()
    for criterion in c_no_descriptors.rubric.criteria:
        for ind in criterion.indicators:
            ind.descriptors = []
    c_no_descriptors.rubric.validate()
    docfile = tmp_path / f"{config_template_path.stem}_no_descriptors.docx"
    generate_rubric(docfile, output_dir, c_no_descriptors)

    # Avec deux niveaux
    c_2_levels = c_no_descriptors.copy()
    c_2_levels.rubric.format.orientation = "portrait"
    c_2_levels.rubric.grade_levels = ["✅", "❌"]
    c_2_levels.rubric.default_grade_weights = [1, 0]
    c_2_levels.rubric.format.columns_width = [None, 3, 3]
    for criterion in c_2_levels.rubric.criteria:
        criterion.default_grade_weights = [1, 0]
        for ind in criterion.indicators:
            ind.grade_weights = [1, 0]
    c_no_descriptors.rubric.validate()
    docfile = tmp_path / f"{config_template_path.stem}_2_levels.docx"
    generate_rubric(docfile, output_dir, c_2_levels)

    # Deux niveaux sans la pondération des indicateurs
    c_2_levels_no_weights = c_2_levels.copy()
    c_2_levels_no_weights.rubric.format.hide_indicators_weight = True
    c_2_levels_no_weights.rubric.validate()
    docfile = tmp_path / f"{config_template_path.stem}_2_levels_no_weights.docx"
    generate_rubric(docfile, output_dir, c_2_levels_no_weights)

def generate_rubric(doc_file: Path, output_dir: Path, config: Config):
    generate_statement_rubric(config.rubric, doc_file, title=config.title())
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)

    # Sur windows, on test aussi la convertion en PDF
    if sys.platform == "win32":
        word_to_pdf(output_path, output_path.with_suffix(".pdf"))
        assert output_path.with_suffix(".pdf").exists()
