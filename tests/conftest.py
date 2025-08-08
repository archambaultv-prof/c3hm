import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from c3hm.data.config.config import Config
from c3hm.data.config.config_parser import from_user_config
from c3hm.data.user_config.config_parser import config_from_yaml


@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def gradebook_path() -> Path:
    """
    Retourne le chemin vers le fichier grille.yaml
    """
    d = Path(__file__).parent / "fixtures"
    return d / "grille.xlsx"

@pytest.fixture
def gradebook2_path() -> Path:
    """
    Retourne le chemin vers le fichier grille_inference.yaml
    """
    d = Path(__file__).parent / "fixtures"
    return d / "grille_inference.xlsx"

@pytest.fixture
def config_full_template_path() -> Path:
    """
    Retourne le chemin vers le fichier de la grille d'évaluation grille.yaml
    """
    d = Path(__file__).parent.parent / "src" / "c3hm" / "assets" / "templates" / "config"
    return d / "grille.yaml"

@pytest.fixture
def config_full_template(config_full_template_path: Path,
                         student_list_csv_path: Path) -> Config:
    """
    Retourne le gabarit complet de la grille d'évaluation.
    """
    user_config = config_from_yaml(config_full_template_path)
    user_config.students = student_list_csv_path
    return from_user_config(user_config)

@pytest.fixture(scope="session")
def output_dir() -> Path:
    """
    Retourne le chemin vers le dossier de sortie pour les tests.
    """
    return Path(__file__).parent / "output"

@pytest.fixture(scope="session", autouse=True)
def clear_output_folder(output_dir: Path):
    """
    Avant la session pytest : supprime puis recrée tests/output
    pour que le dossier soit toujours vide au début.
    """
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def student_list_csv_path() -> Path:
    """
    Retourne le chemin vers le fichier liste_etudiants.csv
    """
    d = Path(__file__).parent / "fixtures"
    return d / "liste_etudiants.csv"
