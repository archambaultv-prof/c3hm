from pathlib import Path

from c3hm.data.config import Config
from c3hm.data.student import read_omnivox_students_file


def generate_gradebook(config: Config, students_file: Path, output_dir: Path) -> None:
    """
    Génère les grilles de correction à partir du fichier de configuration.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")

    students = read_omnivox_students_file(students_file)
    for student in students:
        c = config.model_copy(deep=True)
        c.student_first_name = student.first_name
        c.student_last_name = student.last_name
        c.student_omnivox = student.omnivox_id
        file = output_dir / f"{student.last_name}_{student.first_name}.yaml"
        c.yaml_dump(file)
