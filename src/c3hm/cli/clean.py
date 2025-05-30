from pathlib import Path

import click

from c3hm.commands.clean import PATHS_TO_DELETE, remove_unwanted_dirs


@click.command(
    name="clean",
    help=(
        "Supprime les fichiers et dossiers indésirables (ex. .git, node_modules)\n"
        "dans chaque dossier étudiant sous PATH.\n\n"
        "Un dossier étudiant est un dossier qui respecte le format Omnivox: NOM1_NOM2_12345.\n\n"
        "Exemples:\n"
        "  c3hm clean                     # nettoyage standard dans le répertoire courant\n"
        "  c3hm clean mon_dossier -n      # simulation dans un dossier spécifique\n"
        "  c3hm clean --keep .git --keep .vscode\n"
        "  c3hm clean --all               # scanner tous les dossiers, pas seulement "
        "ceux au format étudiant"
    )
)
@click.argument(
    "path",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        path_type=Path
    ),
    required=True
)
@click.option(
    "--dryrun", "-n",
    is_flag=True,
    default=False,
    help="Simulation : affiche ce qui serait supprimé sans rien toucher. Active le mode verbose."
)
@click.option(
    "--git", "-g",
    is_flag=True,
    default=False,
    help="Supprimer les dossiers .git et .gitignore en plus des autres fichiers indésirables."
)
@click.option(
    "--keep",
    multiple=True,
    help=(
        "Noms ou motifs (glob) à conserver alors qu'ils seraient normalement supprimés. "
        'Exemple : --keep .git'
    )
)
@click.option(
    "--exclude-dir",
    multiple=True,
    help=(
        "Noms ou motifs (glob) de sous-dossiers à exclure du nettoyage. "
        "c3hm ne va pas entrer dans ces dossiers."
    )
)
@click.option(
    "--delete",
    multiple=True,
    help=(
        "Noms ou motifs (glob) de fichiers ou dossiers supplémentaires à supprimer. "
        'Exemple : --delete "*~"'
    )
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Afficher chaque fichier/dossier supprimé"
)
@click.option(
    "--all", "-a",
    "scan_all",
    is_flag=True,
    default=False,
    help=(
        "Scanner tous les fichiers et dossiers dans le répertoire racine, "
        "même ceux qui ne sont pas des dossiers d'étudiants."
    )
)
def clean_command(
    path: Path,
    dryrun: bool,
    keep: tuple[str, ...],
    git: bool,
    exclude_dir: tuple[str, ...],
    delete: tuple[str, ...],
    verbose: bool,
    scan_all: bool,
):
    """
    Supprime les fichiers et dossiers indésirables (ex. .git, node_modules)
    """
    to_delete = PATHS_TO_DELETE
    if delete:
        to_delete.extend(delete)
    if git:
        to_delete.extend([".git", ".gitignore"])
    if keep:
        to_delete = [path for path in to_delete if path not in keep]
    remove_unwanted_dirs(
        root_path=path,
        dryrun=dryrun,
        exclude_dir=list(exclude_dir),
        paths_to_delete=to_delete,
        verbose=verbose,
        scan_all=scan_all,
    )
