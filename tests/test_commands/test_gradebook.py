from pathlib import Path

from c3hm.commands.gradebook import generate_gradebook
from c3hm.data.config import Config
from c3hm.data.student import Student


def test_generate_gradebook(
        config_template_5_path: Path,
        tmp_path: Path,
        output_dir: Path):
    """
    Teste la génération d'un document Excel à partir d'une grille d'évaluation.
    Vérifie que le fichier est créé.

    Recopie le fichier créé dans le répertoire tests/output pour inspection
    manuelle si nécessaire.
    """
    config = Config.from_yaml(config_template_5_path)
    config.students = [
            {"code omnivox": "123456",
             "prénom": "Jean",
             "nom de famille": "Dupont",
             "alias": "jdupont"},
            {"code omnivox": "654321",
             "prénom": "Marie",
             "nom de famille": "Durand",
             "alias": "mdurand"},
            {"code omnivox": "789012",
             "prénom": "Pierre",
             "nom de famille": "Martin",
             "alias": "pmartin"},
    ]
    config.students = [Student.from_dict(student) for student in config.students]

    name = config_template_5_path.with_name(
            f"{config_template_5_path.stem}.xlsx")
    xl_file = tmp_path / name
    generate_gradebook(config, xl_file)
    assert xl_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / xl_file.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    xl_file.replace(output_path)
