import os
import shutil
from pathlib import Path

from c3hm.utils.omnivox import is_student_folder

PATHS_TO_DELETE = [
    "__pycache__",
    ".DS_Store",
    ".idea",
    ".pytest_cache",
    ".venv",
    "venv",
    ".vscode",
    "node_modules",
    "__MACOSX",
]

def is_excluded_dir(path: Path, exclude_dir: list[str]) -> bool:
    """
    Vérifie si le chemin donné correspond à un des motifs d'exclusion.
    """
    return any(path.match(pat) for pat in exclude_dir)

def is_path_to_delete(path: Path, paths_to_delete: list[str]) -> bool:
    """
    Vérifie si le chemin donné correspond à un des motifs de suppression.
    """
    return any(path.match(pat) for pat in paths_to_delete)

def remove_unwanted_dirs(root_path: Path | str = None,
                         paths_to_delete: list[str] = None,
                         exclude_dir: list[str] = None,
                         verbose: bool = False,
                         dryrun: bool = False,
                         scan_all: bool = False) -> None:
    """
    Parcourt chaque dossier étudiant sous root_path et supprime
    tout fichier ou dossier dont le nom apparaît dans l'ensemble
    PATHS_TO_DELETE, modulo les paramètres keep et delete.

    Arguments:
    root_path: Chemin du répertoire racine contenant les dossiers étudiants.
    paths_to_delete: Liste de noms ou motifs (glob) de fichiers ou dossiers à supprimer.
    exclude_dir: Liste de noms ou motifs (glob) de sous-dossiers à exclure du nettoyage.
    verbose: Si True, affiche chaque fichier/dossier supprimé.
    dryrun: Si True, affiche ce qui serait supprimé sans rien toucher.
    scan_all: Si True, scanne tous les fichiers et dossiers dans le répertoire racine,
              même ceux qui ne sont pas des dossiers d'étudiants.
    """
    if root_path is None:
        root_path = Path.cwd()
    root_path = Path(root_path)

    exclude_dir = exclude_dir or []

    paths_to_delete = paths_to_delete or PATHS_TO_DELETE

    if dryrun:
        verbose=True

    if not scan_all:
        # Scan only directories in root_path that qualify as student folders.
        for item in os.listdir(root_path):
            dir_path = root_path / item
            if is_excluded_dir(dir_path, exclude_dir):
                continue
            if is_student_folder(dir_path):
                remove_unwanted_dirs(
                    root_path=dir_path,
                    paths_to_delete=paths_to_delete,
                    exclude_dir=exclude_dir,
                    verbose=verbose,
                    dryrun=dryrun,
                    scan_all=True)
    else:
        # Scan all files and directories in root_path.
        for current_root, dirs, files in os.walk(root_path, topdown=True):
            # Exclude directories that match the exclusion criteria.
            dirs[:] = [
                d for d in dirs
                if not is_excluded_dir(Path(current_root, d), exclude_dir)
            ]

            # Process directories that match the deletion criteria.
            for d in list(dirs):
                d_path = Path(current_root, d)
                if is_path_to_delete(d_path, paths_to_delete):
                    if verbose:
                        print(f"Deleting directory: {d_path}")
                    if not dryrun:
                        shutil.rmtree(d_path)
                    # Remove it from dirs to prevent os.walk from descending into it.
                    dirs.remove(d)
            # Process files that match the deletion criteria.
            for f in list(files):
                f_path = Path(current_root, f)
                if is_path_to_delete(f_path, paths_to_delete):
                    if verbose:
                        print(f"Deleting file: {f_path}")
                    if not dryrun:
                        os.remove(f_path)
