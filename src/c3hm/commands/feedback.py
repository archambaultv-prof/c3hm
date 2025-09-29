from pathlib import Path

from c3hm.commands.rubric.rubric_word import generate_rubric_word
from c3hm.data.config import Config
from c3hm.data.config_parser import check_all_grades, parse_user_config


def generate_feedback(gradebook_path: Path, output_dir: Path):
    """
    Génère un document Word de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """
    configs: list[Config] = []
    for file in gradebook_path.glob("*.yaml"):
        config = parse_user_config(file, include_grading=True, check_grades=False)
        configs.append(config)

    _fill_in_teammates_grades(configs)

    for config in configs:
        check_all_grades(config)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")

    for config in configs:
        p = output_dir / f"{config.student_last_name}_{config.student_first_name}.docx"
        generate_rubric_word(config, p)

def _fill_in_teammates_grades(configs: list[Config]) -> None:
    """
    Remplit les notes des coéquipiers dans chaque configuration.
    """
    known_configs: dict[str, Config] = {}
    duplicate_names: set[str] = set()
    for config in configs:
        for k in (config.student_first_name, config.student_last_name,
                  f"{config.student_first_name} {config.student_last_name}",
                  f"{config.student_last_name} {config.student_first_name}"):
            if k is None:
                continue
            if k in duplicate_names:
                continue
            if k in known_configs:
                del known_configs[k]
                duplicate_names.add(k)
            else:
                known_configs[k] = config

    done: set[str] = set()
    for config in configs:
        for teammate in config.student_teammates:
            if teammate in known_configs:
                target_config = known_configs[teammate]
                if target_config.get_student_full_name() in done:
                    raise ValueError(f"La configuration de {target_config.student_first_name} "
                                     f"{target_config.student_last_name} a déjà été ajustée "
                                     f"depuis un autre coéquipier.")
                done.add(target_config.get_student_full_name())
                copy_grades_to(config, target_config)
            if teammate in duplicate_names:
                raise ValueError(f"Le nom de coéquipier '{teammate}' est ambigu dans la "
                                 f"configuration de {config.student_first_name} "
                                 f"{config.student_last_name}.")

def copy_grades_to(source: Config, target: Config) -> None:
    """
    Copie les notes des critères et indicateurs de `source` vers `target`.
    """
    if target.evaluation_grade is None:
        target.evaluation_grade = source.evaluation_grade
    if target.evaluation_comment is None:
        target.evaluation_comment = source.evaluation_comment
    for source_criterion, target_criterion in zip(source.criteria, target.criteria, strict=True):
        if source_criterion.name != target_criterion.name:
            raise ValueError(f"Les critères '{source_criterion.name}' et "
                             f"'{target_criterion.name}' ne correspondent pas.")
        if target_criterion.grade is None:
            target_criterion.grade = source_criterion.grade
        if target_criterion.comment is None:
            target_criterion.comment = source_criterion.comment
        for source_indicator, target_indicator in zip(source_criterion.indicators,
                                                     target_criterion.indicators, strict=True):
            if source_indicator.name != target_indicator.name:
                raise ValueError(f"Les indicateurs '{source_indicator.name}' et "
                                 f"'{target_indicator.name}' ne correspondent pas.")
            if target_indicator.grade is None:
                target_indicator.grade = source_indicator.grade
            if target_indicator.comment is None:
                target_indicator.comment = source_indicator.comment
