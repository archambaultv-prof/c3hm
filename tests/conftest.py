from pathlib import Path

import pytest


@pytest.fixture
def rubric_1_path():
    """
    Retourne le chemin vers le fichier YAML de la grille d'évaluation 1.
    """
    return Path(__file__).parent / "fixtures" / "rubric_1.yaml"
