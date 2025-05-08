import shutil
from pathlib import Path

import pytest


@pytest.fixture
def gradebook_path() -> Path:
    """
    Retourne le chemin vers le fichier gradebook_1.yaml
    """
    d = Path(__file__).parent / "fixtures"
    return d / "grille_gradebook.xlsx"

@pytest.fixture
def config_template_path() -> Path:
    """
    Retourne le chemin vers le fichier de la grille d'évaluation config_5_levels.yaml
    """
    d = Path(__file__).parent.parent / "src" / "c3hm" / "assets" / "templates" / "config"
    return d / "grille.yaml"

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
