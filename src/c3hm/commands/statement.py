from pathlib import Path

from c3hm.commands.generate_rubric import generate_rubric


def generate_statement_rubric(
        rubric,
        output_path: Path | str,
        *,
        title: str = "Grille d'évaluation") -> None:
    """
    Génère la grille d'évaluation sous format Word pour les énoncés.
    """
    generate_rubric(rubric=rubric, output_path=output_path, title=title)
