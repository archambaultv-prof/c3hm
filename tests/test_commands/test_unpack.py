import shutil
import zipfile
from pathlib import Path

import pytest

from c3hm.commands.unpack import PATHS_TO_DELETE, UnpackOmnivox


@pytest.fixture
def temp_zip(tmp_path: Path):
    """
    Crée une structure de répertoires et fichiers temporaires pour les tests.
    """
    root = tmp_path / "test_unpack"
    root.mkdir()
    for code in ["1234567", "7654321", "2345678"]:
        student_dir = root / f"student_{code}_TP1_Remis_le_2025-06-30_12h00m00s"
        student_dir.mkdir()
        if code == "1234567":
            # Structure a aplatir
            (student_dir / "subdir1").mkdir()
            (student_dir / "subdir1" / "subdir2").mkdir()
            current_dir = student_dir / "subdir1" / "subdir2"
        else:
            current_dir = student_dir
        (current_dir / "subdir1").mkdir() # This folder has the same name as one to be flattened
        (current_dir / "subdir1" / "file.txt").write_text("Boom !")
        (current_dir / "python.py").write_text(f"print('Hello from {code}')\n")
        (current_dir / "node_modules").mkdir()
        (current_dir / "node_modules" / "package.json").write_text(
            '{"name": "example", "version": "1.0.0"}\n'
        )
        (current_dir / "extra_file.txt").write_text("This is an extra file.")
        (current_dir / ".git").mkdir()
        (current_dir / ".git" / "config").write_text("[core]\n    repositoryformatversion = 0\n")

        # Zip the student_dir
        zip_file = student_dir.with_suffix(".zip")
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in current_dir.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(student_dir))

        # Delete the original directory after zipping
        shutil.rmtree(student_dir)

    zip_file = root.with_suffix(".zip")
    with zipfile.ZipFile(zip_file, 'w') as zf:
        for file in root.glob("**/*"):
            if file.is_file():
                zf.write(file, file.relative_to(root))
    # Supprimer le répertoire racine après la création du zip
    shutil.rmtree(root)

    return zip_file

def test_unpack(temp_zip: Path, output_dir: Path):
    """
    Teste la décompression des archives dans le dossier temporaire.
    """
    # Copie le fichier dans le répertoire de sortie pour inspection manuelle
    output_path = output_dir / temp_zip.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(temp_zip, output_path)

    unpacker = UnpackOmnivox(folder=temp_zip, paths_to_delete=PATHS_TO_DELETE, verbose=False)
    unpacker.unpack()
    assert output_dir.exists(), "Le dossier de sortie n'a pas été créé."

    unpacked_folder = temp_zip.parent / temp_zip.stem
    shutil.copytree(unpacked_folder, output_dir / temp_zip.stem)
