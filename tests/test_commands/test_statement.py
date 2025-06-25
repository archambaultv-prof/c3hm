from decimal import Decimal
from pathlib import Path

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
    c_1.rubric.format.show_indicators_percent = False
    c_1.rubric.validate_rubric()
    doc_file = tmp_path / f"{config_template_path.stem}_no_weights.docx"
    generate_rubric(doc_file, output_dir, c_1)

    # Avec deux niveaux
    c_2_levels = c_1.copy()
    c_2_levels.rubric.format.orientation = "portrait"
    c_2_levels.rubric.grade_levels = ["✅", "❌"]
    c_2_levels.rubric.grade_thresholds = [(Decimal(1), Decimal(1), Decimal(1)),
                                          (Decimal(0), Decimal(0), Decimal(0))]
    c_2_levels.rubric.default_descriptors = ["", ""]
    for criterion in c_2_levels.rubric.criteria:
        for indicator in criterion.indicators:
            indicator.descriptors = []
    c_2_levels.rubric.format.columns_width = [None, 3, 3]
    c_2_levels.rubric.validate_rubric()
    docfile = tmp_path / f"{config_template_path.stem}_2_levels.docx"
    generate_rubric(docfile, output_dir, c_2_levels)


def generate_rubric(doc_file: Path, output_dir: Path, config: Config):
    generate_statement_rubric(config.rubric, doc_file, title=config.title())
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)

    # # Sur windows, on test aussi la convertion en PDF
    # if sys.platform == "win32":
    #     word_to_pdf(output_path, output_path.with_suffix(".pdf"))
    #     assert output_path.with_suffix(".pdf").exists()
