from pathlib import Path

import pytest

from c3hm.commands.clean import is_excluded_dir, is_path_to_delete, remove_unwanted_dirs


@pytest.fixture
def students_paths():
    """
    Fournit une liste de chemins pour créer des fichiers et répertoires temporaires.
    """
    return [
        {"path": "xyz_314159/__pycache__", "type": "folder"},
        {"path": "xyz_314159/file1.txt", "type": "file"},
        {"path": "xyz_314159/.DS_Store", "type": "file"},
        {"path": "xyz_314159/file2.txt", "type": "file"},
        {"path": "abc_271828/__pycache__", "type": "folder"},
        {"path": "abc_271828/file1.txt", "type": "file"},
        {"path": "abc_271828/.DS_Store", "type": "file"},
        {"path": "abc_271828/file2.txt", "type": "file"},
        {"path": "abc_271828/sub_folder/.git", "type": "folder"},
        {"path": "bar_161803/__pycache__", "type": "folder"},
        {"path": "bar_161803/file1.txt", "type": "file"},
        {"path": "bar_161803/.DS_Store", "type": "file"},
        {"path": "bar_161803/file2.txt", "type": "file"},
        {"path": "not_student_dir/__pycache__", "type": "folder"},
        {"path": "not_student_dir/file1.txt", "type": "file"},
        {"path": "not_student_dir/.DS_Store", "type": "file"},
        {"path": "not_student_dir/file2.txt", "type": "file"},
    ]

@pytest.fixture
def temp_dir(tmp_path: Path, students_paths: list[dict]):
    """
    Crée une structure de répertoires et fichiers temporaires pour les tests.
    """
    for entry in students_paths:
        full_path: Path = tmp_path / entry["path"]
        if entry["type"] == "file":
            full_path.touch()
        else:
            full_path.mkdir(parents=True)

    return tmp_path

def test_is_excluded_dir():
    """
    Teste la fonction is_excluded_dir pour vérifier les exclusions.
    """
    exclude_dir = ["bar_161803", "foo_*"]
    assert is_excluded_dir(Path("bar_161803"), exclude_dir) is True
    assert is_excluded_dir(Path("hello/bar_161803"), exclude_dir) is True
    assert is_excluded_dir(Path("foo_12345"), exclude_dir) is True
    assert is_excluded_dir(Path("hello/foo_12345"), exclude_dir) is True
    assert is_excluded_dir(Path("baz_12345"), exclude_dir) is False

def test_is_path_to_delete():
    """
    Teste la fonction is_path_to_delete pour vérifier les exclusions.
    """
    path_to_delete = [".git", "node_mudules", "*.pyc"]
    assert is_path_to_delete(Path(".git"), path_to_delete) is True
    assert is_path_to_delete(Path("hello/.git"), path_to_delete) is True
    assert is_path_to_delete(Path("node_mudules"), path_to_delete) is True
    assert is_path_to_delete(Path("hello/node_mudules"), path_to_delete) is True
    assert is_path_to_delete(Path("abc.pyc"), path_to_delete) is True
    assert is_path_to_delete(Path("hello/abc.pyc"), path_to_delete) is True
    assert is_path_to_delete(Path("baz_12345"), path_to_delete) is False

def test_remove_unwanted_dirs(temp_dir: Path, students_paths: list[dict]):
    """
    Teste la suppression des fichiers et dossiers indésirables.
    """
    root_path = temp_dir
    paths_to_delete = ["__pycache__", ".DS_Store", ".git"]
    exclude_dir = ["bar_161803"]

    # Exécuter la fonction avec dryrun pour vérifier les fichiers ciblés
    remove_unwanted_dirs(
        root_path=root_path,
        paths_to_delete=paths_to_delete,
        exclude_dir=exclude_dir,
        verbose=True,
        dryrun=True
    )

    for entry in students_paths:
        full_path = temp_dir / entry["path"]
        assert full_path.exists(), f"{entry['path']} should not be deleted."

    # Exécuter la fonction sans dryrun pour effectuer la suppression
    remove_unwanted_dirs(
        root_path=root_path,
        paths_to_delete=paths_to_delete,
        exclude_dir=exclude_dir,
        verbose=True,
        dryrun=False
    )

    paths_to_delete = [
        "xyz_314159/__pycache__",
        "xyz_314159/.DS_Store",
        "abc_271828/__pycache__",
        "abc_271828/.DS_Store",
        "abc_271828/sub_folder/.git"
    ]
    for entry in paths_to_delete:
        full_path: Path = temp_dir / entry
        assert not full_path.exists(), f"{entry['path']} should be deleted."

    for entry in students_paths:
        if entry["path"] not in paths_to_delete:
            full_path = temp_dir / entry["path"]
            assert full_path.exists(), f"{entry['path']} should not be deleted."
