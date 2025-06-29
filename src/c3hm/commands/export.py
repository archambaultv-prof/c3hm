from pathlib import Path

from c3hm.models.generate_rubric import generate_rubric


def export_rubric(
        rubric,
        output_path: Path | str) -> None:
    """
    Génère la grille d'évaluation sous format Word pour les énoncés.
    """
    generate_rubric(rubric=rubric, output_path=output_path)
