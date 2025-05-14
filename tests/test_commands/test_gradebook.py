from pathlib import Path

from c3hm.commands.gradebook import generate_gradebook
from c3hm.data.config import Config


def test_generate_gradebook(
        config_template_path: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Teste la génération d'un document Excel à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    config = Config.from_yaml(config_template_path)

    create_gradebook_file(config_template_path, tmp_path, output_dir, config)


def create_gradebook_file(config_template_path: Path, tmp_path: Path,
                          output_dir: Path, config: Config):
    name = config_template_path.with_name(
            f"{config_template_path.stem}.xlsx")
    xl_file = tmp_path / name
    generate_gradebook(config, xl_file)
    assert xl_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / xl_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    xl_file.replace(output_path)


def test_bug_1(
        config_bug_1: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Test pour un problème de formule Excel pour les indicateurs.
    """
    config = Config.from_yaml(config_bug_1)

    create_gradebook_file(config_bug_1, tmp_path, output_dir, config)
