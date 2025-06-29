from pathlib import Path

from c3hm.commands.template import export_template


def test_export_template(
    tmp_path: Path,
    output_dir: Path
    ):
    """
    Teste l'exportation du modèle de configuration.
    """
    # Appelle la fonction export_template
    tmp_file = tmp_path / "grille_template.yaml"
    config_file = output_dir / "config" / "grille_template.yaml"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    export_template(output_path=tmp_file)
    # Vérifie que le fichier a été créé
    assert tmp_file.exists()

    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    tmp_file.replace(config_file)
