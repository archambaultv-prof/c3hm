from pathlib import Path
from c3hm.commands.init import export_template
from c3hm.data.config import Config


def test_export_template(
    tmp_path: Path,
    output_dir: Path
    ):
    """
    Teste l'exportation du modèle de configuration.
    """
    # Appelle la fonction export_template
    for t in ["default", "basic", "full"]:
        tmp_file = tmp_path / f"{t}.yaml"
        config_file = output_dir / "config" / f"{t}.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        export_template(output_path=tmp_file, template=t)
        # Vérifie que le fichier a été créé
        assert tmp_file.exists()

        # Copie le fichier dans le répertoire de sortie pour inspection manuelle
        tmp_file.replace(config_file)
