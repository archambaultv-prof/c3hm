from decimal import Decimal
from pathlib import Path

from c3hm.commands.export.export_rubric import export_rubric
from c3hm.data.config.config import Config
from c3hm.data.config.grade_level import GradeLevel


def test_generate_word_from_rubric(
        config_full_template: Config,
        config_full_template_path: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Teste la génération d'un document Word à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    # Test avec le gabarit
    config = config_full_template
    doc_file = tmp_path / config_full_template_path.with_suffix(".docx")
    generate_rubric(doc_file, output_dir, config)

    # Test avec le gabarit avec pondération des indicateurs
    c_1 = config.model_copy(deep=True)
    c_1.format.show_indicators_points = True
    doc_file = tmp_path / f"{config_full_template_path.stem}_with_points.docx"
    generate_rubric(doc_file, output_dir, c_1)

    # Avec deux niveaux
    c_2_levels = config.model_copy(deep=True)
    c_2_levels.format.orientation = "portrait"
    c_2_levels.evaluation.grade_levels = [GradeLevel(
            name="✅",
            maximum=Decimal(100),
            minimum=Decimal(60)
        ),
        GradeLevel(
            name="❌",
            maximum=Decimal(59),
            minimum=Decimal(0)
        )]
    c_2_levels.format.show_grade_level_descriptions = False
    c_2_levels.format.show_indicators_points = True
    for criterion in c_2_levels.evaluation.criteria:
        for indicator in criterion.indicators:
            indicator.descriptors = ["" for _ in c_2_levels.evaluation.grade_levels]
    c_2_levels.format.columns_width = [None, 4, 4]
    docfile = tmp_path / f"{config_full_template_path.stem}_2_levels.docx"
    generate_rubric(docfile, output_dir, c_2_levels)


def generate_rubric(doc_file: Path, output_dir: Path, config: Config):
    export_rubric(config, doc_file)
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)

