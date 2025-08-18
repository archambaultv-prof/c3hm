from pathlib import Path

from c3hm.commands.export.export_word import generate_rubric_word
from c3hm.data.config.config import Config


def export_rubric(
        config: Config,
        output_path: Path | str) -> None:
    """
    Génère la grille d'évaluation sous format Word pour les énoncés.
    """
    generate_rubric_word(config=config, output_path=output_path)
