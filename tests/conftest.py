import shutil
from pathlib import Path

import pytest


@pytest.fixture
def rubric_1_path() -> Path:
    """
    Retourne le chemin vers le fichier YAML de la grille d'évaluation 1.
    """
    return Path(__file__).parent / "fixtures" / "rubric_1.yaml"

@pytest.fixture
def rubric_template_5_path() -> Path:
    """
    Retourne le chemin vers le fichier YAML de la grille d'évaluation grille_5_niveaux.yaml.
    """
    return Path(__file__).parent.parent / "gabarits_grilles" / "grille_5_niveaux.yaml"

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
