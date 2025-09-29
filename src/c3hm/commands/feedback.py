from pathlib import Path

from c3hm.commands.rubric.rubric_word import generate_rubric_word
from c3hm.data.config import Config
from c3hm.data.config_parser import parse_user_config


def generate_feedback(gradebook_path: Path, output_dir: Path):
    """
    Génère un document Word de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """
    configs: list[Config] = []
    for file in gradebook_path.glob("*.yaml"):
        config = parse_user_config(file, include_grading=True, check_grades=False)
        configs.append(config)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")

    for config in configs:
        p = output_dir / f"{config.student_last_name}_{config.student_first_name}.docx"
        generate_rubric_word(config, p)
