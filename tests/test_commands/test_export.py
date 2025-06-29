from decimal import Decimal
from pathlib import Path

from c3hm.commands.export.export import export_rubric
from c3hm.data.config import Config
from c3hm.data.rubric.grade_level import GradeLevel
from c3hm.data.rubric.grade_levels import GradeLevels


def test_generate_word_from_rubric(
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
    config = Config.from_user_config(config_full_template_path)
    doc_file = tmp_path / config_full_template_path.with_suffix(".docx")
    generate_rubric(doc_file, output_dir, config)

    # Test avec le gabarit avec pondération des indicateurs
    c_1 = config.copy()
    c_1.rubric.format.show_indicators_points = True
    doc_file = tmp_path / f"{config_full_template_path.stem}_with_points.docx"
    generate_rubric(doc_file, output_dir, c_1)

    # Avec deux niveaux
    c_2_levels = config.copy()
    c_2_levels.rubric.format.orientation = "portrait"
    c_2_levels.rubric.grade_levels = GradeLevels(
        levels=[GradeLevel(
            name="✅",
            max_percentage=Decimal(100),
            min_percentage=Decimal(60)
        ),
        GradeLevel(
            name="❌",
            max_percentage=Decimal(59),
            min_percentage=Decimal(0)
        )])
    c_2_levels.rubric.format.show_level_descriptions = False
    c_2_levels.rubric.format.show_indicators_points = True
    for criterion in c_2_levels.rubric.evaluation.criteria:
        for indicator in criterion.indicators:
            for level in c_2_levels.rubric.grade_levels.levels:
                c_2_levels.rubric.descriptors.set_descriptor(indicator, level, "")
    c_2_levels.rubric.format.columns_width = [None, 4, 4]
    docfile = tmp_path / f"{config_full_template_path.stem}_2_levels.docx"
    generate_rubric(docfile, output_dir, c_2_levels)


def generate_rubric(doc_file: Path, output_dir: Path, config: Config):
    export_rubric(config.rubric, doc_file)
    assert doc_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / doc_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_file.replace(output_path)

